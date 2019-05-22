# import Env
import os, sys
from collections import Counter
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from convert_datetime import dt_from_14digits_to_iso, shift_seconds
from save_pfvinfo_sta import *
from pymongo import *
client = MongoClient()
db = client.nm4bd

DATA_INTERVAL = 60 # データの間隔
STAY_SEC_TH = 60 # 滞留時間の基準値
STAY_JUD_TH = 30 # 滞留判定を行うまでの時間
INTERVAL = 5 # データ取得間隔

def data_sorting(st,ed):
    # 該当期間のデータを消去
    db.modpfvinfo.remove({"datetime":{"$gte":st,"$lte":ed}})
    db.modstayinfo.remove({"datetime":{"$gte":st,"$lte":ed}})
    # 該当期間に更新されたmacの取り出し
    # maclist = ["00:11:81:10:01:0e"]
    # maclist = ["b0:72:bf:4a:76:c9","00:11:81:10:01:00","00:11:81:10:01:1b"]
    maclist = []
    maclist += db.pastdata.find({},{"mac":1,"_id":0})

    for mac in maclist:
        mac = mac["mac"]
        # 対象macの移動・滞留データの取り出し
        data = []
        data += db.pfvmacinfo.find({"$and":[{"datetime":{"$gte":st,"$lte":ed}},{"mac":mac}]},{"_id":0})
        data += db.staymacinfo.find({"$and":[{"datetime":{"$gte":st,"$lte":ed}},{"mac":mac}]},{"_id":0})
        if len(data) == 0:
            continue
        # 取り出したデータを時刻順にソート
        keyfunc_time = lambda x:x["datetime"]
        data = sorted(data,key=keyfunc_time)  # 時刻をキーとして昇順にソート
        update_dt = 0 # 最新の過去データの取得時刻
        ap_list_flow =[] # 1データ分（remake対象）のAPのリスト
        pre_floor = 0 # 前の時刻のフロア
        for time in data:
            if update_dt==0:
                start_dt = time["datetime"]  # remakeを行う開始時刻
            elif ((time["datetime"] - update_dt).seconds > DATA_INTERVAL) or (time["floor"] != pre_floor):  # 過去データの取得時刻からDATA_INTERVAL秒経過している（長時間データが取れていない）か、フロア変更時
                remake_data(mac,start_dt,update_dt,ap_list_flow,pre_floor)  # 一旦過去データの取得時刻までremakeを行う
                start_dt = time["datetime"] # 開始時刻更新
                ap_list_flow =[] # 1データ分のAPのリスト
            if "pcwl_id" in time:  # 滞留の場合(staymacinfo)
                ap_list_flow.append({"pcwl_id":time["pcwl_id"],"datetime":time["datetime"]})
            elif "route" in time:  # 移動の場合(pfvmacinfo)
                for i in range(len(time["route"])):
                    if ap_list_flow == []:  # remake対象の先頭の場合
                        ap_list_flow.append({"pcwl_id":time["route"][i][0],"datetime":time["datetime"]})  # route = [[12,26],[26,9]]の時は、スタートノードの12を追加
                    ap_list_flow.append({"pcwl_id":time["route"][i][1],"datetime":time["datetime"]})  # route = [[12,26],[26,9]]の時は、終了ノードの26(i=0)or9(i=1)を追加
            update_dt = time["datetime"]
            pre_floor = time["floor"]
        remake_data(mac,start_dt,update_dt,ap_list_flow,pre_floor)

def  remake_data(mac,st,ed,flow,floor):
    flow_ap_list = [] # 時刻を付与したAPのリスト(移動時)
    stay_ap_list = [] # 時刻を付与したAPのリスト(滞留時)
    tmp_ap_list = []
    stay_jud_list = [] # 滞留の判定に用いるデータのリスト（{"pcwl_id":0,"cnt":0,"start":0,"last":0(,"real_id":1つ飛びの場合)}）
    index_cnt = 0 # ループ中のカウント
    key_id = lambda x:x["pcwl_id"] # リストからidだけ取り出す際に使用
    # 時系列の移動・滞留データをループ
    for i in flow:
        if tmp_ap_list == []:
            tmp_ap_list.append({"datetime":i["datetime"],"pcwl_id":i["pcwl_id"]})
            continue
        index_cnt += 1
        if i["pcwl_id"] in list(map(key_id,stay_jud_list)): # 最終滞留時刻の更新
            jud_index = list(map(key_id,stay_jud_list)).index(i["pcwl_id"])
            stay_jud_list[jud_index]["last"] = i["datetime"]
            stay_jud_list[jud_index]["last_index"] = index_cnt
            del stay_jud_list[jud_index+1:]
        elif (tmp_ap_list[-1]["pcwl_id"] == i["pcwl_id"]) or ((len(tmp_ap_list)>=2) and (tmp_ap_list[-2]["pcwl_id"] == i["pcwl_id"])): # 滞留判定を開始するかを判定
            if tmp_ap_list[-1]["pcwl_id"] == i["pcwl_id"]: # 連続の場合
                stay_jud_list.append({"pcwl_id":i["pcwl_id"],"start":i["datetime"],"last":i["datetime"],"real_id":i["pcwl_id"],"start_index":index_cnt,"last_index":index_cnt})
            else: # 1つ飛びの場合
                if len(stay_jud_list) == 0: # 滞留判定が存在しない場合は追加
                    stay_jud_list.append({"pcwl_id":i["pcwl_id"],"start":tmp_ap_list[-1]["datetime"],"last":i["datetime"],"real_id":tmp_ap_list[-1]["pcwl_id"],"start_index":index_cnt,"last_index":index_cnt})
                elif stay_jud_list[-1]["last_index"] < len(tmp_ap_list) - 1: # 滞留判定期間が重複していない場合も追加
                    stay_jud_list.append({"pcwl_id":i["pcwl_id"],"start":tmp_ap_list[-1]["datetime"],"last":i["datetime"],"real_id":tmp_ap_list[-1]["pcwl_id"],"start_index":index_cnt,"last_index":index_cnt})
                else: # 滞留判定期間が重複している場合は追加しない
                    pass
        if (len(stay_jud_list)!=0)and(i["datetime"] - stay_jud_list[0]["last"]).seconds>STAY_JUD_TH:
            next_node = []
            next_node += db.pcwlnode.find({"$and":[{"floor":floor},{"pcwl_id":stay_jud_list[0]["pcwl_id"]}]})
            if i["pcwl_id"] in next_node[0]["next_id"]: # 隣接ノードでは判定に移行しない
                tmp_ap_list.append({"datetime":i["datetime"],"pcwl_id":i["pcwl_id"]})
                continue
            # 最大で遡るインデックス決定
            if len(stay_ap_list) == 0:
                reverse_index = 0
            else:
                reverse_index = stay_ap_list[-1]["end_index"]
            mod_jud_info = stay_jud_list[0]
            for ap in reversed(tmp_ap_list[reverse_index:stay_jud_list[0]["start_index"]-1]): # 直前の移動まで遡り最初に出現した時刻を求める
                if (mod_jud_info["start"]-ap["datetime"]).seconds > STAY_JUD_TH:
                    break
                else:
                    if ap["pcwl_id"] == mod_jud_info["pcwl_id"]:
                        mod_jud_info["start"] = ap["datetime"]
                        stay_jud_list[0]["start_index"] = tmp_ap_list.index({"datetime":ap["datetime"],"pcwl_id":ap["pcwl_id"]})+1
                        stay_jud_list[0]["start"] = tmp_ap_list[stay_jud_list[0]["start_index"]]["datetime"]
                        stay_jud_list[0]["real_id"] = tmp_ap_list[stay_jud_list[0]["start_index"]]["pcwl_id"]
            start_index = stay_jud_list[0]["start_index"]
            end_index = stay_jud_list[0]["last_index"]
            if (stay_jud_list[0]["last"] - stay_jud_list[0]["start"]).seconds<STAY_SEC_TH:
                pass
            else:
                if len(stay_ap_list) == 0:
                    tmp_start = stay_jud_list[0]["start"]
                    for ap in reversed(tmp_ap_list[:start_index-1]):
                        if (tmp_start - ap["datetime"]).seconds > STAY_JUD_TH:
                            break
                        else:
                            if ap["pcwl_id"] == stay_jud_list[0]["real_id"]:
                                tmp_start = ap["datetime"]
                                start_index = tmp_ap_list.index({"datetime":tmp_start,"pcwl_id":ap["pcwl_id"]}) + 1
                    route = []
                    for ap in tmp_ap_list[:start_index]:
                        route.append(ap)
                    if len(route) > 1:
                        if (tmp_ap_list[start_index-1]["datetime"] - tmp_ap_list[0]["datetime"]).seconds <= 10: # 最初の移動にかかる時間が10秒以下の場合
                            stay_start_time = tmp_ap_list[0]["datetime"]
                        else:
                            flow_ap_list.append({"start":tmp_ap_list[0]["datetime"],"end":tmp_ap_list[start_index-1]["datetime"],"route":route,"start_index":0,"end_index":start_index-1})
                            if tmp_ap_list[start_index-1]["datetime"] == tmp_ap_list[start_index]["datetime"]:
                                stay_start_time = shift_seconds(tmp_ap_list[start_index]["datetime"],5)
                            else:
                                stay_start_time = tmp_ap_list[start_index]["datetime"]
                    else:
                        start_index -= 1
                        stay_start_time = tmp_ap_list[start_index]["datetime"]
                else: # 滞留のリストに既にデータが存在している場合
                    flow_start_index = stay_ap_list[-1]["end_index"]
                    flow_start_time = shift_seconds(tmp_ap_list[flow_start_index]["datetime"],5)
                    if flow_start_time > tmp_ap_list[start_index-1]["datetime"]:
                        flow_end_time = flow_start_time
                    else:
                        flow_end_time = tmp_ap_list[start_index-1]["datetime"]
                    route = []
                    for ap in tmp_ap_list[flow_start_index:start_index]:
                        route.append(ap)

                    flow_ap_list.append({"start":flow_start_time,"end":flow_end_time,"route":route,"start_index":flow_start_index,"end_index":start_index-1})
                    if flow_end_time == tmp_ap_list[start_index]["datetime"]:
                        stay_start_time = shift_seconds(tmp_ap_list[start_index]["datetime"],5)
                    else:
                        stay_start_time = tmp_ap_list[start_index]["datetime"]
                stay_ap_list.append({"start":stay_start_time,"end":tmp_ap_list[end_index]["datetime"],"pcwl_id":stay_jud_list[0]["pcwl_id"],"real_id":stay_jud_list[0]["real_id"],"start_index":start_index,"end_index":end_index})
            del stay_jud_list[0]
        tmp_ap_list.append({"datetime":i["datetime"],"pcwl_id":i["pcwl_id"]})

    # 未処理の滞留判定を処理
    for stay_jud in stay_jud_list:
        start_index = stay_jud["start_index"]
        end_index = stay_jud["last_index"]
        if (stay_jud["last"] - stay_jud["start"]).seconds<STAY_SEC_TH:
            pass
        else:
            if len(stay_ap_list) == 0:
                route = []
                for ap in tmp_ap_list[:start_index]:
                    route.append(ap)
                if len(route) > 1:
                    if (tmp_ap_list[start_index-1]["datetime"] - tmp_ap_list[0]["datetime"]).seconds <= 10: # 最初の移動にかかる時間が10秒以下の場合
                        stay_start_time = tmp_ap_list[0]["datetime"]
                    else:
                        flow_ap_list.append({"start":tmp_ap_list[0]["datetime"],"end":tmp_ap_list[start_index-1]["datetime"],"route":route,"start_index":0,"end_index":start_index-1})
                        if tmp_ap_list[start_index-1]["datetime"] == tmp_ap_list[start_index]["datetime"]:
                            stay_start_time = shift_seconds(tmp_ap_list[start_index]["datetime"],5)
                        else:
                            stay_start_time = tmp_ap_list[start_index]["datetime"]
                else:
                    start_index -= 1
                    stay_start_time = tmp_ap_list[start_index]["datetime"]
            else: # 滞留のリストに既にデータが存在している場合
                flow_start_index = stay_ap_list[-1]["end_index"]
                flow_start_time = shift_seconds(tmp_ap_list[flow_start_index]["datetime"],5)
                if flow_start_time > tmp_ap_list[start_index-1]["datetime"]:
                    flow_end_time = flow_start_time
                else:
                    flow_end_time = tmp_ap_list[start_index-1]["datetime"]
                route = []
                for ap in tmp_ap_list[flow_start_index:start_index]:
                    route.append(ap)
                flow_ap_list.append({"start":flow_start_time,"end":flow_end_time,"route":route,"start_index":flow_start_index,"end_index":start_index-1})
                if flow_end_time == tmp_ap_list[start_index]["datetime"]:
                    stay_start_time = shift_seconds(tmp_ap_list[start_index]["datetime"],5)
                else:
                    stay_start_time = tmp_ap_list[start_index]["datetime"]
            stay_ap_list.append({"start":stay_start_time,"end":tmp_ap_list[end_index]["datetime"],"pcwl_id":stay_jud["pcwl_id"],"real_id":stay_jud["real_id"],"start_index":start_index,"end_index":end_index})

    # 未処理のtmp_ap_listの処理
    if len(stay_ap_list) == 0:
        route = []
        for ap in tmp_ap_list:
            route.append(ap)
        flow_ap_list.append({"start":tmp_ap_list[0]["datetime"],"end":tmp_ap_list[-1]["datetime"],"route":route,"start_index":0,"end_index":len(flow)-1})
    elif tmp_ap_list[-1]["datetime"] > stay_ap_list[-1]["end"]:
        flow_start_index = stay_ap_list[-1]["end_index"]
        flow_start_time = shift_seconds(tmp_ap_list[flow_start_index]["datetime"],5)
        if flow_start_time > tmp_ap_list[start_index-1]["datetime"]:
            flow_end_time = flow_start_time
        else:
            flow_end_time = tmp_ap_list[start_index-1]["datetime"]
        route = []
        for ap in tmp_ap_list[flow_start_index:]:
            route.append(ap)
        flow_ap_list.append({"start":flow_start_time,"end":flow_end_time,"route":route,"start_index":flow_start_index,"end_index":len(flow)-1})

    del_stay_list = []

    # 滞留情報の補正
    for stay_info in stay_ap_list:
        if len(stay_ap_list) == 0:
            break
        stay_info["floor"] = floor
        stay_info["mac"] = mac
        stay_info_index = stay_ap_list.index(stay_info)
        start_index = stay_info["start_index"]
        end_index = stay_info["end_index"]
        part_stay_list = flow[start_index:end_index+1]
        # 滞留中の出現回数確認
        appear_list = list(map(key_id,part_stay_list))
        appear_cnt = Counter(appear_list).most_common(10)
        prev_flow_index = None
        next_flow_index = None
        for flow_info in reversed(flow_ap_list): # 直前の移動データを参照
            if flow_info["end"] <= stay_info["start"]:
                prev_flow_index = flow_ap_list.index(flow_info)
                if len(flow_ap_list) > prev_flow_index + 1:
                    next_flow_index = prev_flow_index + 1
                else:
                    next_flow_index = None
                break
            next_flow_index = 0

        if (len(appear_cnt) >= 5) and (appear_cnt[0][1]/len(part_stay_list) <= 0.5):
            del_stay_list.append(stay_info)
            route = []
            for ap in tmp_ap_list[flow_ap_list[prev_flow_index]["start_index"]:flow_ap_list[next_flow_index]["end_index"]+1]:
                route.append(ap)
            flow_ap_list.insert(prev_flow_index,{"start":flow_ap_list[prev_flow_index]["start"],"end":flow_ap_list[next_flow_index]["end"],"start_index":flow_ap_list[prev_flow_index]["start_index"],"end_index":flow_ap_list[next_flow_index]["end_index"],"route":route})
            del flow_ap_list[prev_flow_index+1:prev_flow_index+3]
            continue


        # 出現数が同値の場合の対象期間の前後を最大5つまでを対象期間に加え、再度出現頻度の判定を行う
        if len(appear_cnt)>1 and appear_cnt[0][1] == appear_cnt[1][1]:
            mod_start_index = start_index - min(start_index,5)
            mod_end_index = end_index + min((len(tmp_ap_list)-1 - end_index),5)
            mod_part_stay_list = flow[mod_start_index:mod_end_index+1]
            appear_list = list(map(key_id,mod_part_stay_list)) # 対象期間のリストの再生成
            appear_cnt = Counter(appear_list).most_common(5) # 出現数を再カウント

        if (stay_info["pcwl_id"] != appear_cnt[0][0]) and (appear_cnt[0][1] > appear_cnt[1][1]): # 対象のAPが期間内出現回数1位のAPと異なる場合
            for ap in part_stay_list: # 期間内で最初に最多APが出現した時間を参照
                if ap["pcwl_id"] == appear_cnt[0][0]:
                    mod_ap_index = tmp_ap_list.index(ap)
                    mod_ap_info_start = {"datetime":ap["datetime"],"pcwl_id":ap["pcwl_id"]} # 最初の出現データ保存用
                    mod_ap_info_end = {"datetime":ap["datetime"],"pcwl_id":ap["pcwl_id"]} # 最後の出現データ保存用
                    break
            if prev_flow_index == None:
                reverse = reversed(tmp_ap_list[:mod_ap_index])
            else:
                reverse = reversed(tmp_ap_list[flow_ap_list[prev_flow_index]["start_index"]:mod_ap_index])
            for ap in reverse: # 期間外まで遡り最初に出現した時刻を求める
                if (mod_ap_info_start["datetime"]-ap["datetime"]).seconds > STAY_JUD_TH:
                    break
                else:
                    if ap["pcwl_id"] == mod_ap_info_start["pcwl_id"]:
                        mod_ap_info_start["datetime"] = ap["datetime"]
            for ap in tmp_ap_list[mod_ap_index+1:]:
                if ((ap["datetime"]-mod_ap_info_end["datetime"]).seconds > STAY_JUD_TH) and (ap["pcwl_id"] != appear_cnt[1][0]) and (ap["pcwl_id"] != appear_cnt[0][0]):
                    break
                else:
                    if ap["pcwl_id"] == mod_ap_info_end["pcwl_id"]:
                        mod_ap_info_end["datetime"] = ap["datetime"]
            # 滞留情報の更新
            stay_info["pcwl_id"] = appear_cnt[0][0] # 滞留箇所を変更
            stay_info["start_index"] = tmp_ap_list.index(mod_ap_info_start)+1
            stay_info["end_index"] = tmp_ap_list.index(mod_ap_info_end)
            stay_info["start"] = tmp_ap_list[stay_info["start_index"]]["datetime"]
            stay_info["end"] = tmp_ap_list[stay_info["end_index"]]["datetime"]
            stay_info["real_id"] = tmp_ap_list[stay_info["start_index"]]["pcwl_id"]
            if stay_info["start"] == tmp_ap_list[stay_info["start_index"]-1]["datetime"]:
                stay_info["start"] = shift_seconds(stay_info["start"],5)

            # 滞留直前の移動を適切な形に変更
            if (prev_flow_index != None) and (stay_info["start_index"]-1 <= flow_ap_list[prev_flow_index]["end_index"]):
                flow_ap_list[prev_flow_index]["end"] = tmp_ap_list[stay_info["start_index"]-1]["datetime"]
                route = []
                for tmp_route in tmp_ap_list[flow_ap_list[prev_flow_index]["start_index"]-1:stay_info["start_index"]]:
                    route.append(tmp_route)
                flow_ap_list[prev_flow_index]["route"] = route
                flow_ap_list[prev_flow_index]["end_index"] = stay_info["start_index"]-1
            elif prev_flow_index == None:
                route = []
                for tmp_route in tmp_ap_list[:stay_info["start_index"]]:
                    route.append(tmp_route)
                if len(route) != 1:
                    flow_ap_list.insert(0,{"start":tmp_ap_list[0]["datetime"],"start_index":0,"end_index":stay_info["start_index"]-1,"end":tmp_ap_list[stay_info["start_index"]-1]["datetime"],"route":route})
                    next_flow_index += 1
                else:
                    stay_info["start_index"] = tmp_ap_list.index(mod_ap_info_start)
                    stay_info["start"] = tmp_ap_list[stay_info["start_index"]]["datetime"]
                    stay_info["real_id"] = tmp_ap_list[stay_info["start_index"]]["pcwl_id"]
            else:
                flow_ap_list[prev_flow_index]["end"] = tmp_ap_list[stay_info["start_index"]-1]["datetime"]
                for ap in tmp_ap_list[flow_ap_list[prev_flow_index]["end_index"]:stay_info["start_index"]]:
                    flow_ap_list[prev_flow_index]["route"].append(ap)
                flow_ap_list[prev_flow_index]["end_index"] = stay_info["start_index"]-1
            # 滞留直後の移動を適切な形に変更
            if (next_flow_index != None) and (stay_info["end_index"] >= flow_ap_list[next_flow_index]["end_index"]):
                del flow_ap_list[next_flow_index]
                if (len(stay_ap_list) > stay_info_index + 1) and (stay_info["pcwl_id"] == stay_ap_list[stay_info_index+1]["pcwl_id"]):
                    del stay_ap_list[stay_info_index+1] # １つ後の滞留データを破棄する
                elif (len(stay_ap_list) > stay_info_index + 1) and (stay_info["pcwl_id"] != stay_ap_list[stay_info_index+1]["pcwl_id"]):
                    if len(flow_ap_list) >= next_flow_index:
                        flow_ap_list[next_flow_index]["start"] = tmp_ap_list[stay_info["end_index"]+1]["datetime"]
                        len_route = -len(flow_ap_list[next_flow_index]["route"])
                        for ap in tmp_ap_list[stay_info["end_index"]:flow_ap_list[next_flow_index]["start_index"]]:
                            flow_ap_list[next_flow_index]["route"].insert(len_route,ap)
                        flow_ap_list[next_flow_index]["start_index"] = stay_info["end_index"]+1
                    else:
                        route = []
                        for tmp_route in tmp_ap_list[stay_info["end_index"]:stay_ap_list[stay_info_index+1]["end_index"]+1]:
                            route.append(tmp_route)
                        flow_ap_list.insert(next_flow_index,{"start":tmp_ap_list[stay_info["end_index"]+1]["datetime"],"end":stay_ap_list[stay_info_index+1]["end"],"start_index":stay_info["end_index"]+1,"end_index":stay_ap_list[stay_info_index+1]["end_index"],"route":route})

                # if len(flow_ap_list[next_flow_index]["route"]) < 2: # 次の移動データが移動データとしての状態にない場合
                #     if len(stay_ap_list) > stay_info_index + 1: # 滞留データがまだ存在している場合
                #         stay_info["end"] = stay_ap_list[stay_info_index+1]["end"] # 処理中の滞留データの終了時刻を1つ後の滞留データの終了時刻に変更する
                #         del stay_ap_list[stay_info_index+1] # １つ後の滞留データを破棄する
                #     else: # 処理中の滞留データが最後の滞留データである場合
                #         stay_info["end"] = flow_ap_list[next_flow_index]["end"] # 処理中の滞留データの終了時刻を次の移動データの終了時刻に変更する
                #     del flow_ap_list[next_flow_index] # 次の移動データを破棄する
                # else: # 次の移動データが正しく存在している場合


            elif (next_flow_index != None) and (stay_info["end_index"] >= flow_ap_list[next_flow_index]["start_index"]):
                flow_ap_list[next_flow_index]["route"] = []
                for tmp_route in tmp_ap_list[stay_info["end_index"]:flow_ap_list[next_flow_index]["end_index"]+1]:
                    flow_ap_list[next_flow_index]["route"].append(tmp_route)
                flow_ap_list[next_flow_index]["start"] = shift_seconds(stay_info["end"],5)
                flow_ap_list[next_flow_index]["start_index"] = stay_info["end_index"]+1
            elif next_flow_index == None:
                route = []
                for tmp_route in tmp_ap_list[stay_info["end_index"]:]:
                    route.append(tmp_route)
                if prev_flow_index == None:
                    flow_ap_list.insert(0,{"start":tmp_ap_list[stay_info["end_index"]+1]["datetime"],"end":tmp_ap_list[-1]["datetime"],"start_index":stay_info["end_index"]+1,"end_index":len(tmp_ap_list)-1,"route":route})
                else:
                    flow_ap_list.insert(prev_flow_index+1,{"start":tmp_ap_list[stay_info["end_index"]+1]["datetime"],"end":tmp_ap_list[-1]["datetime"],"start_index":stay_info["end_index"]+1,"end_index":len(tmp_ap_list)-1,"route":route})
            else:
                flow_ap_list[next_flow_index]["start"] = tmp_ap_list[stay_info["end_index"]+1]["datetime"]
                len_route = -len(flow_ap_list[next_flow_index]["route"])
                for ap in tmp_ap_list[stay_info["end_index"]:flow_ap_list[next_flow_index]["start_index"]]:
                    flow_ap_list[next_flow_index]["route"].insert(len_route,ap)
                flow_ap_list[next_flow_index]["start_index"] = stay_info["end_index"]+1
        else: # 異なっていない場合も直前のデータは確認する
            if prev_flow_index == None:
                continue
            else:
                mod_ap_info_start = {"datetime":stay_info["start"],"pcwl_id":stay_info["pcwl_id"],"start_index":stay_info["start_index"]} # 最初の出現データ保存用
                for ap in reversed(tmp_ap_list[flow_ap_list[prev_flow_index]["start_index"]:stay_info["start_index"]-1]): # 直前の移動まで遡り最初に出現した時刻を求める
                    if (mod_ap_info_start["datetime"]-ap["datetime"]).seconds > STAY_JUD_TH:
                        break
                    else:
                        if ap["pcwl_id"] == mod_ap_info_start["pcwl_id"]:
                            mod_ap_info_start["datetime"] = ap["datetime"]
                            mod_ap_info_start["start_index"] = tmp_ap_list.index(ap)
                if stay_info["start_index"] != mod_ap_info_start["start_index"]:
                    stay_info["start_index"] = mod_ap_info_start["start_index"]+1
                    stay_info["start"] = tmp_ap_list[stay_info["start_index"]]["datetime"]
                    stay_info["real_id"] = tmp_ap_list[stay_info["start_index"]]["pcwl_id"]
                    # 滞留直前の移動を適切な形に変更
                    flow_ap_list[prev_flow_index]["route"] = []
                    for tmp_route in tmp_ap_list[flow_ap_list[prev_flow_index]["start_index"]:stay_info["start_index"]]:
                        flow_ap_list[prev_flow_index]["route"].append(tmp_route)
                    if len(flow_ap_list[prev_flow_index]["route"]) < 2:
                        stay_info["start_index"] -= 1
                        stay_info["start"] = tmp_ap_list[stay_info["start_index"]]["datetime"]
                        stay_info["real_id"] = tmp_ap_list[stay_info["start_index"]]["pcwl_id"]
                    else:
                        flow_ap_list[prev_flow_index]["end"] = tmp_ap_list[stay_info["start_index"]-1]["datetime"]
                        stay_info["start"] = shift_seconds(tmp_ap_list[stay_info["start_index"]-1]["datetime"],5)

    # 不要staydataの除去
    for del_data in del_stay_list:
        stay_ap_list.remove(del_data)

    # 移動情報の補正・最初と最後の移動データの統合判定
    for flow_info in flow_ap_list[:]:
        # 不要情報の除去
        if "start_index" in flow_info:
            del flow_info["start_index"]
        if "end_index" in flow_info:
            del flow_info["end_index"]
        # 必要情報の付与
        flow_info["floor"] = floor
        flow_info["mac"] = mac
        # 移動情報の補正
        route = []
        back_count = 0 # 往復しているノード数
        back_flag = False # 往復状態を保持するフラグ
        center_ap = 0 # 往復の折り返しノードを保持する変数
        for ap in flow_info["route"]:
            if len(route) == 0:
                route.append(ap)
            elif route[-1]["pcwl_id"] == ap["pcwl_id"]:
                # if back_flag == False:
                route[-1]["datetime"] = ap["datetime"]
            elif back_flag:
                if (len(route) >= 2 + back_count*2) and (route[-(2 + back_count*2)]["pcwl_id"] == ap["pcwl_id"]): # 往復状態の継続
                    if center_ap == ap["pcwl_id"]:
                        if ((ap["datetime"] - route[-2 - back_count*2]["datetime"]).seconds <= INTERVAL*(2*back_count)) or (back_count == 1):
                            del route[-2 - back_count*2:]
                        back_count = 0
                        back_flag = False
                        center_ap = 0
                    elif ((route[-1]["datetime"] - route[-1 - back_count*2]["datetime"]).seconds <= INTERVAL*back_count):
                        del route[-1 - back_count*2:-1]
                        back_count = 1
                        center_ap = route[-1]
                    else:
                        back_count += 1
                elif ((route[-1]["datetime"] - route[-1 - back_count*2]["datetime"]).seconds <= INTERVAL*(2*back_count+1)) or (back_count == 1): # 往復状態終了時点における経過時間から往復したか判定
                    del route[-1 - back_count*2:-1]
                    back_flag = False
                    back_count = 0
                    center_ap = 0
                elif (len(route) >= 2) and (route[-2]["pcwl_id"] == ap["pcwl_id"]):
                    back_count = 1
                    center_ap = route[-1]["pcwl_id"]
                else:
                    back_flag = False
                    back_count = 0
                    center_ap = 0
                route.append(ap)
            elif (len(route) >= 2) and (route[-2]["pcwl_id"] == ap["pcwl_id"]):
                back_flag = True
                back_count = 1
                center_ap = route[-1]["pcwl_id"]
                route.append(ap)
            else:
                route.append(ap)
        else: # for文終了時に往復判定中のものが残っている場合
            if back_flag and ((route[-1]["datetime"] - route[-1 - back_count*2]["datetime"]).seconds <= INTERVAL*(2*back_count)): # 往復状態終了時点における経過時間から往復したか判定(ループ終了時に往復状態にある場合)
                del route[-1 - back_count*2:-1]
        if len(route) < 2: # 判定の結果route情報が1件分しか残らなかった場合は移動のリストから除去
            flow_ap_list.remove(flow_info)
            continue
        else:
            flow_info["route"] = route
            print(list(map(key_id,route)))

    analyze_flow(flow_ap_list)

    make_modpfvinfo(flow_ap_list,db.modpfvinfo,INTERVAL)
    make_modstayinfo(stay_ap_list,db.modstayinfo,INTERVAL)
    print("mac: "+mac+" / st: "+str(st)+" / ed: "+str(ed))
    # print(list(map(key_id,flow)))
    print("flow------------------------------------------------------------------------")
    # print(flow_ap_list)
    print("stay------------------------------------------------------------------------")
    print(stay_ap_list)
    print("----------------------------------------------------------------------------")

def analyze_flow(flow_ap_list):
    for flow in flow_ap_list:
        for i in range(1,len(flow["route"])):
            go_ap = db.floor_analyze.find_one({"pcwl_id":flow["route"][i-1]["pcwl_id"],"floor":flow["floor"]})
            go_ap["go"][str(flow["route"][i]["pcwl_id"])] += 1
            go_ap["go"]["total"] += 1
            come_ap = db.floor_analyze.find_one({"pcwl_id":flow["route"][i]["pcwl_id"],"floor":flow["floor"]})
            come_ap["come"][str(flow["route"][i-1]["pcwl_id"])] += 1
            come_ap["come"]["total"] += 1
            db.floor_analyze.save(go_ap)
            db.floor_analyze.save(come_ap)
            if i > 1:
                tran_ap = db.floor_analyze.find_one({"pcwl_id":flow["route"][i-2]["pcwl_id"],"floor":flow["floor"]})
                tran_ap["transition"][str(flow["route"][i-1]["pcwl_id"])][str(flow["route"][i]["pcwl_id"])] += 1
                tran_ap["transition"][str(flow["route"][i-1]["pcwl_id"])]["total"] += 1
                db.floor_analyze.save(tran_ap)



if __name__ == '__main__':
    st = dt_from_14digits_to_iso(20170920182730)
    ed = dt_from_14digits_to_iso(20170920183730)
    data_sorting(st,ed)
