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

STAY_SEC_TH = 45 # 滞留時間の基準値
STAY_JUD_TH = 45 # 滞留判定を行うまでの時間
INTERVAL = 5 # データ取得間隔

def remake_data(st,ed):
    # 該当期間に更新されたmacの取り出し
    # maclist = ["00:11:81:10:01:00"]
    # maclist = ["b0:72:bf:4a:76:c9"]
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
        data = sorted(data,key=keyfunc_time)

        update_dt = 0 # 最終更新時刻
        ap_list_flow =[] # 1データ分のAPのリスト
        ap_list_stay = []
        flow_cnt = 0 # 移動数カウント
        stay_cnt = 0 # 滞留数カウント
        pre_floor = 0 # 前の時刻ののフロア
        for time in data:
            if update_dt==0:
                start_dt = time["datetime"]
            else:
                if ((time["datetime"] - update_dt).seconds >30) or (time["floor"] != pre_floor):
                    print_result(mac,start_dt,update_dt,ap_list_flow,ap_list_stay,flow_cnt,stay_cnt,pre_floor)
                    start_dt = time["datetime"] # 開始時刻更新
                    ap_list_flow =[] # 1データ分のAPのリスト
                    ap_list_stay = []
                    flow_cnt = 0 # 移動数カウント
                    stay_cnt = 0 # 滞留数カウント
            if "pcwl_id" in time:
                stay_cnt += 1
                ap_list_flow.append({"pcwl_id":time["pcwl_id"],"datetime":time["datetime"]})
                ap_list_stay.append(time["pcwl_id"])
            elif "route" in time:
                flow_cnt += 1
                for i in range(len(time["route"])):
                    if ap_list_flow == []:
                        ap_list_flow.append({"pcwl_id":time["route"][i][0],"datetime":time["datetime"]})
                    ap_list_flow.append({"pcwl_id":time["route"][i][1],"datetime":time["datetime"]})
                    # if i == 0:
                    #     ap_list_flow.append({"pcwl_id":time["route"][i][0],"datetime":time["datetime"]})
                    #     ap_list_flow.append({"pcwl_id":time["route"][i][1],"datetime":time["datetime"]})
                    # else:
                    #     ap_list_flow.append({"pcwl_id":time["route"][i][1],"datetime":time["datetime"]})
                # print(ap_list_flow)
                # print(time["route"])
            update_dt = time["datetime"]
            pre_floor = time["floor"]
        print_result(mac,start_dt,update_dt,ap_list_flow,ap_list_stay,flow_cnt,stay_cnt,pre_floor)

def  print_result(mac,st,ed,flow,stay,flow_cnt,stay_cnt,floor):
    flow_ap_list = [] # 時刻を付与したAPのリスト(移動時)
    stay_ap_list = [] # 時刻を付与したAPのリスト(滞留時)
    tmp_ap_list = []
    stay_jud_list = [] # 滞留の判定に用いるデータのリスト（{"pcwl_id":0,"cnt":0,"start":0,"last":0(,"real_id":1つ飛びの場合)}）
    key_id = lambda x:x["pcwl_id"]

    # 時系列の移動・滞留データをループ
    for i in flow:
        if tmp_ap_list != []:
            if i["pcwl_id"] in list(map(key_id,stay_jud_list)): # 最終滞留時刻の更新
                index = list(map(key_id,stay_jud_list)).index(i["pcwl_id"])
                stay_jud_list[index]["last"] = i["datetime"]
                del stay_jud_list[index+1:]
            else:
                # if (tmp_ap_list[-1]["pcwl_id"] == i["pcwl_id"]) or (cnt["pcwl_id"] == i["pcwl_id"]):
                if (tmp_ap_list[-1]["pcwl_id"] == i["pcwl_id"]) or ((len(tmp_ap_list)>=2) and (tmp_ap_list[-2]["pcwl_id"] == i["pcwl_id"])): # 滞留判定を開始するかを判定
                    if tmp_ap_list[-1]["pcwl_id"] == i["pcwl_id"]: # 連続の場合
                        stay_jud_list.append({"pcwl_id":i["pcwl_id"],"start":i["datetime"],"last":i["datetime"]})
                    else: # 1つ飛びの場合
                        if len(stay_jud_list) == 0: # 滞留判定が存在しない場合は追加
                            stay_jud_list.append({"pcwl_id":i["pcwl_id"],"start":tmp_ap_list[-1]["datetime"],"last":i["datetime"],"real_id":tmp_ap_list[-1]["pcwl_id"]})
                        elif tmp_ap_list.index({"datetime":stay_jud_list[-1]["last"],"pcwl_id":stay_jud_list[-1]["pcwl_id"]}) < len(tmp_ap_list) - 1: # 滞留判定期間が重複していない場合も追加
                            stay_jud_list.append({"pcwl_id":i["pcwl_id"],"start":tmp_ap_list[-1]["datetime"],"last":i["datetime"],"real_id":tmp_ap_list[-1]["pcwl_id"]})
                        else: # 滞留判定期間が重複している場合は追加しない
                            pass
                elif (len(stay_jud_list)!=0)and(i["datetime"] - stay_jud_list[0]["last"]).seconds>STAY_JUD_TH:
                    if "real_id" in stay_jud_list[0]:
                        start_index = tmp_ap_list.index({"datetime":stay_jud_list[0]["start"],"pcwl_id":stay_jud_list[0]["real_id"]})
                        Ap_id = stay_jud_list[0]["real_id"]
                    else:
                        start_index = tmp_ap_list.index({"datetime":stay_jud_list[0]["start"],"pcwl_id":stay_jud_list[0]["pcwl_id"]})
                        Ap_id = stay_jud_list[0]["pcwl_id"]
                    end_index = tmp_ap_list.index({"datetime":stay_jud_list[0]["last"],"pcwl_id":stay_jud_list[0]["pcwl_id"]})

                    if (stay_jud_list[0]["last"] - stay_jud_list[0]["start"]).seconds<STAY_SEC_TH:
                        tmp_ap_list[start_index-1]["datetime"] = tmp_ap_list[end_index]["datetime"]
                        del tmp_ap_list[start_index:end_index+1]
                    else:
                        if len(stay_ap_list) == 0:
                            tmp_start = stay_jud_list[0]["start"]
                            for ap in reversed(tmp_ap_list[:start_index]):
                                if (tmp_start - ap["datetime"]).seconds > STAY_JUD_TH:
                                    break
                                else:
                                    if ap["pcwl_id"] == Ap_id:
                                        tmp_start = ap["datetime"]
                                        start_index = tmp_ap_list.index({"datetime":tmp_start,"pcwl_id":Ap_id}) + 1
                            route = []
                            for j in tmp_ap_list[:start_index]:
                                route.append(j["pcwl_id"])
                            # start_index -= 1
                            if len(route) > 1:
                                flow_ap_list.append({"start":tmp_ap_list[0]["datetime"],"end":tmp_ap_list[start_index-1]["datetime"],"route":route,"start_index":0,"end_index":start_index-1})
                                if tmp_ap_list[start_index-1]["datetime"] == tmp_ap_list[start_index]["datetime"]:
                                    for ap in tmp_ap_list[start_index+1]:
                                        if ap["datetime"] > tmp_ap_list[start_index-1]["datetime"]:
                                            break
                                        start_index += 1
                                # stay_ap_list.append({"start":stay_jud_list[start_index]["datetime"],"end":[end_index]["datetime"],"pcwl_id":stay_jud_list[0]["pcwl_id"]})
                            else:
                                start_index -= 1
                            stay_ap_list.append({"start":tmp_ap_list[start_index]["datetime"],"end":tmp_ap_list[end_index]["datetime"],"pcwl_id":stay_jud_list[0]["pcwl_id"]})
                        else: # 滞留のリストに既にデータが存在している場合
                            flow_start_index = tmp_ap_list.index({"datetime":stay_ap_list[-1]["end"],"pcwl_id":stay_ap_list[-1]["pcwl_id"]})
                            flow_start_time = shift_seconds(tmp_ap_list[flow_start_index]["datetime"],5)
                            tmp_start = stay_jud_list[0]["start"]
                            # reverse_list = tmp_ap_list[flow_start_index+1:start_index]
                            for ap in reversed(tmp_ap_list[flow_start_index+1:start_index]):
                                if (tmp_start - ap["datetime"]).seconds > STAY_JUD_TH:
                                    break
                                else:
                                    if ap["pcwl_id"] == Ap_id:
                                        tmp_start = ap["datetime"]
                                        start_index = tmp_ap_list.index({"datetime":tmp_start,"pcwl_id":Ap_id}) + 1
                            # if tmp_ap_list[flow_start_index]["datetime"] == tmp_ap_list[flow_start_index+1]["datetime"]: # 前回の滞留終了時刻と移動開始時刻が同一か判定
                            #     change_time_flag = True
                            # else:
                            #     flow_start_time = tmp_ap_list[flow_start_index+1]["datetime"]
                            #     change_time_flag = False
                            route = []
                            for j in tmp_ap_list[flow_start_index:start_index]:
                                route.append(j["pcwl_id"])
                                # if change_time_flag:
                                #     if tmp_ap_list[flow_start_index]["datetime"] < j["datetime"]:
                                #         flow_start_time = j["datetime"]
                                #         change_time_flag = False
                            # if change_time_flag:
                            #     flow_start_time = tmp_ap_list[flow_start_index]["datetime"]

                            flow_ap_list.append({"start":flow_start_time,"end":tmp_ap_list[start_index-1]["datetime"],"route":route,"start_index":flow_start_index,"end_index":start_index-1})
                            if tmp_ap_list[start_index-1]["datetime"] == tmp_ap_list[start_index]["datetime"]:
                                for ap in tmp_ap_list[start_index+1]:
                                    if ap["datetime"] > tmp_ap_list[start_index-1]["datetime"]:
                                        break
                                    start_index += 1
                            stay_ap_list.append({"start":tmp_ap_list[start_index]["datetime"],"end":tmp_ap_list[end_index]["datetime"],"pcwl_id":stay_jud_list[0]["pcwl_id"]})
                    del stay_jud_list[0]
        tmp_ap_list.append({"datetime":i["datetime"],"pcwl_id":i["pcwl_id"]})

    # 未処理の滞留判定を処理
    for stay_jud in stay_jud_list:
        if "real_id" in stay_jud:
            start_index = tmp_ap_list.index({"datetime":stay_jud["start"],"pcwl_id":stay_jud["real_id"]})
        else:
            start_index = tmp_ap_list.index({"datetime":stay_jud["start"],"pcwl_id":stay_jud["pcwl_id"]})
        end_index = tmp_ap_list.index({"datetime":stay_jud["last"],"pcwl_id":stay_jud["pcwl_id"]})
        if (stay_jud["last"] - stay_jud["start"]).seconds<STAY_SEC_TH:
            tmp_ap_list[start_index-1]["datetime"] = tmp_ap_list[end_index]["datetime"]
            del tmp_ap_list[start_index:end_index+1]
        else:
            if len(stay_ap_list) == 0:
                route = []
                for j in tmp_ap_list[:start_index]:
                    route.append(j["pcwl_id"])
                if len(route) > 1:
                    flow_ap_list.append({"start":tmp_ap_list[0]["datetime"],"end":tmp_ap_list[start_index-1]["datetime"],"route":route,"start_index":0,"end_index":start_index-1})
                    if tmp_ap_list[start_index-1]["datetime"] == tmp_ap_list[start_index]["datetime"]:
                        for ap in tmp_ap_list[start_index+1]:
                            if ap["datetime"] > tmp_ap_list[start_index-1]["datetime"]:
                                break
                            start_index += 1
                else:
                    start_index -= 1
                stay_ap_list.append({"start":tmp_ap_list[start_index]["datetime"],"end":tmp_ap_list[end_index]["datetime"],"pcwl_id":stay_jud["pcwl_id"]})
            else: # 滞留のリストに既にデータが存在している場合
                flow_start_index = tmp_ap_list.index({"datetime":stay_ap_list[-1]["end"],"pcwl_id":stay_ap_list[-1]["pcwl_id"]})
                flow_start_time = shift_seconds(tmp_ap_list[flow_start_index]["datetime"],5)
                # if tmp_ap_list[flow_start_index]["datetime"] == tmp_ap_list[flow_start_index+1]["datetime"]: # 前回の滞留終了時刻と移動開始時刻が同一か判定
                #     change_time_flag = True
                # else:
                #     flow_start_time = tmp_ap_list[flow_start_index+1]["datetime"]
                #     change_time_flag = False
                route = []
                for j in tmp_ap_list[flow_start_index:start_index]:
                    route.append(j["pcwl_id"])
                #     if change_time_flag:
                #         if tmp_ap_list[flow_start_index]["datetime"] < j["datetime"]:
                #             flow_start_time = j["datetime"]
                #             change_time_flag = False
                # if change_time_flag:
                #     flow_start_time = tmp_ap_list[flow_start_index]["datetime"]
                flow_ap_list.append({"start":flow_start_time,"end":tmp_ap_list[start_index-1]["datetime"],"route":route,"start_index":flow_start_index,"end_index":start_index-1})
                if tmp_ap_list[start_index-1]["datetime"] == tmp_ap_list[start_index]["datetime"]:
                    for ap in tmp_ap_list[start_index+1]:
                        if ap["datetime"] > tmp_ap_list[start_index-1]["datetime"]:
                            break
                        start_index += 1
                stay_ap_list.append({"start":tmp_ap_list[start_index]["datetime"],"end":tmp_ap_list[end_index]["datetime"],"pcwl_id":stay_jud["pcwl_id"]})

    # 未処理のtmp_ap_listの処理
    if len(stay_ap_list) == 0:
        route = []
        for i in tmp_ap_list:
            route.append(i["pcwl_id"])
        flow_ap_list.append({"start":tmp_ap_list[0]["datetime"],"end":tmp_ap_list[-1]["datetime"],"route":route,"start_index":0,"end_index":-1})
    elif tmp_ap_list[-1]["datetime"] > stay_ap_list[-1]["end"]:
        flow_start_index = tmp_ap_list.index({"datetime":stay_ap_list[-1]["end"],"pcwl_id":stay_ap_list[-1]["pcwl_id"]})
        flow_start_time = shift_seconds(tmp_ap_list[flow_start_index]["datetime"],5)
        # if tmp_ap_list[flow_start_index]["datetime"] == tmp_ap_list[flow_start_index+1]["datetime"]: # 前回の滞留終了時刻と移動開始時刻が同一か判定
        #     change_time_flag = True
        # else:
        #     flow_start_time = tmp_ap_list[flow_start_index+1]["datetime"]
        #     change_time_flag = False
        route = []
        for j in tmp_ap_list[flow_start_index:]:
            route.append(j["pcwl_id"])
        #     if change_time_flag:
        #         if tmp_ap_list[flow_start_index]["datetime"] < j["datetime"]:
        #             flow_start_time = j["datetime"]
        #             change_time_flag = False
        # if change_time_flag:
        #     flow_start_time = tmp_ap_list[flow_start_index]["datetime"]
        flow_ap_list.append({"start":flow_start_time,"end":tmp_ap_list[-1]["datetime"],"route":route,"start_index":flow_start_index,"end_index":-1})

    # 滞留情報の補正
    for stay_info in stay_ap_list:
        if len(stay_ap_list) == 0:
            break
        stay_info["floor"] = floor
        stay_info["mac"] = mac
        stay_info_index = stay_ap_list.index(stay_info)
        start_index = tmp_ap_list.index({"datetime":stay_info["start"],"pcwl_id":stay_info["pcwl_id"]})
        end_index = tmp_ap_list.index({"datetime":stay_info["end"],"pcwl_id":stay_info["pcwl_id"]})
        part_stay_list = tmp_ap_list[start_index:end_index+1]
        # 滞留中の出現回数確認
        appear_list = list(map(key_id,part_stay_list))
        appear_cnt = Counter(appear_list).most_common(2)
        if (stay_info["pcwl_id"] != appear_cnt[0][0]) and (appear_cnt[0][1] > appear_cnt[1][1]): # 対象のAPが期間内出現回数1位のAPと異なる場合
            prev_flow_index = None
            next_flow_index = None
            for flow_info in reversed(flow_ap_list): # 直前の移動データを参照
                if flow_info["end"] <= stay_info["start"]:
                    prev_flow_index = flow_ap_list.index({"start":flow_info["start"],"end":flow_info["end"],"route":flow_info["route"],"start_index":flow_info["start_index"],"end_index":flow_info["end_index"]})
                    if len(flow_ap_list) > prev_flow_index + 1:
                        next_flow_index = prev_flow_index + 1
                    else:
                        next_flow_index = None
                    break
                next_flow_index = 0

            for ap in part_stay_list: # 期間内で最初に最多APが出現した時間を参照
                if ap["pcwl_id"] == appear_cnt[0][0]:
                    # mod_ap_info = {"datetime":ap["datetime"],"pcwl_id":ap["pcwl_id"]}
                    mod_ap_index = tmp_ap_list.index({"datetime":ap["datetime"],"pcwl_id":ap["pcwl_id"]})
                    mod_ap_info_start = {"datetime":ap["datetime"],"pcwl_id":ap["pcwl_id"]} # 最初の出現データ保存用
                    mod_ap_info_end = {"datetime":ap["datetime"],"pcwl_id":ap["pcwl_id"]} # 最後の出現データ保存用
                    break
            for ap in reversed(tmp_ap_list[:mod_ap_index]): # 期間外まで遡り最初に出現した時刻を求める
                if (mod_ap_info_start["datetime"]-ap["datetime"]).seconds > STAY_JUD_TH:
                    break
                else:
                    if ap["pcwl_id"] == mod_ap_info_start["pcwl_id"]:
                        mod_ap_info_start["datetime"] = ap["datetime"]
            for ap in tmp_ap_list[mod_ap_index+1:]:
                if (ap["datetime"]-mod_ap_info_end["datetime"]).seconds > STAY_JUD_TH:
                    break
                else:
                    if ap["pcwl_id"] == mod_ap_info_end["pcwl_id"]:
                        mod_ap_info_end["datetime"] = ap["datetime"]
            stay_info["pcwl_id"] = appear_cnt[0][0] # 滞留箇所を変更
            stay_info["start"] = tmp_ap_list[tmp_ap_list.index(mod_ap_info_start)+1]["datetime"]
            stay_info["end"] = tmp_ap_list[tmp_ap_list.index(mod_ap_info_end)]["datetime"]

            # 滞留直前の移動を適切な形に変更
            if (prev_flow_index != None) and (tmp_ap_list.index(mod_ap_info_start) <= flow_ap_list[prev_flow_index]["end_index"]):
                flow_ap_list[prev_flow_index]["end"] = tmp_ap_list[tmp_ap_list.index(mod_ap_info_start)]["datetime"]
                route = flow_ap_list[prev_flow_index]["route"]
                for tmp_route in reversed(route):
                    if tmp_route == stay_info["pcwl_id"]:
                        break
                    del flow_ap_list[prev_flow_index]["route"][-1]
            elif prev_flow_index == None:
                route = []
                for tmp_route in tmp_ap_list[:tmp_ap_list.index(mod_ap_info_start)+1]:
                    route.append(tmp_route)
                if len(route) != 1:
                    flow_ap_list.insert(0,{"start":tmp_ap_list[0]["datetime"],"end":tmp_ap_list[tmp_ap_list.index(mod_ap_info_start)]["datetime"],"route":route})
                else:
                    stay_info["start"] = tmp_ap_list[tmp_ap_list.index(mod_ap_info_start)]["datetime"]
            else:
                flow_ap_list[prev_flow_index]["end"] = tmp_ap_list[tmp_ap_list.index(mod_ap_info_start)]["datetime"]
                for ap in tmp_ap_list[flow_ap_list[prev_flow_index]["end_index"]+1:tmp_ap_list.index(mod_ap_info_start)+1]:
                    flow_ap_list[prev_flow_index]["route"].append(ap["pcwl_id"])
            # 滞留直後の移動を適切な形に変更
            if (next_flow_index != None) and (tmp_ap_list.index(mod_ap_info_end) >= flow_ap_list[next_flow_index]["start_index"]):
                flow_ap_list[next_flow_index]["start"] = tmp_ap_list[tmp_ap_list.index(mod_ap_info_end)+1]["datetime"]
                route = flow_ap_list[next_flow_index]["route"]
                for tmp_route in range(len(route)):
                    if route[tmp_route] == stay_info["pcwl_id"]:
                        del flow_ap_list[next_flow_index]["route"][:tmp_route]
                        if len(route) < 2:
                            if len(stay_ap_list) > stay_info_index + 1:
                                stay_info["end"] = stay_ap_list[stay_info_index+1]["end"]
                                del stay_ap_list[stay_info_index+1]
                            else:
                                stay_info["end"] = flow_ap_list[next_flow_index]["end"]
                            del flow_ap_list[next_flow_index]
                        break
            elif next_flow_index == None:
                route = []
                for tmp_route in tmp_ap_list[tmp_ap_list.index(mod_ap_info_end):]:
                    route.append(tmp_route)
                flow_ap_list.insert(0,{"start":tmp_ap_list[tmp_ap_list.index(mod_ap_info_end)+1]["datetime"],"end":tmp_ap_list[-1]["datetime"],"route":route})
            else:
                flow_ap_list[next_flow_index]["start"] = tmp_ap_list[tmp_ap_list.index(mod_ap_info_end)+1]["datetime"]
                print(tmp_ap_list[tmp_ap_list.index(mod_ap_info_end)])
                len_route = -len(flow_ap_list[next_flow_index]["route"])
                for ap in tmp_ap_list[tmp_ap_list.index(mod_ap_info_end):flow_ap_list[next_flow_index]["start_index"]]:
                    flow_ap_list[next_flow_index]["route"].insert(len_route,ap["pcwl_id"])

    # 移動情報の補正
    for flow_info in flow_ap_list:
        del flow_info["start_index"]
        del flow_info["end_index"]
        flow_info["floor"] = floor
        flow_info["mac"] = mac
        route = []
        for ap in flow_info["route"]:
            if len(route) == 0:
                route.append(ap)
            elif route[-1] == ap:
                pass
            elif (len(route) >= 2) and (route[-2] == ap):
                del route[-1]
            else:
                route.append(ap)
        flow_info["route"] = route

    make_modpfvinfo(flow_ap_list,db.modpfvinfo,INTERVAL)
    make_modstayinfo(stay_ap_list,db.modstayinfo,INTERVAL)
    tmp = Counter(stay)
    print(mac)
    print(st)
    print(ed)
    # print(flow)
    # print(tmp_ap_list)
    print("flow------------------------------------------------------------------------")
    print(flow_ap_list)
    print("stay------------------------------------------------------------------------")
    print(stay_ap_list)
    # print(tmp_ap_list)
    # print(tmp.most_common(5))
    # print("滞留割合："+str(round(stay_cnt/(stay_cnt+flow_cnt)*100,2)))
    # print("AP"+str(tmp.most_common(5)[0][0])+"滞留率:"+str(round(tmp.most_common(5)[0][1]/len(stay)*100,2))+"%")
    print("----------------------------------------------------------------------------")

if __name__ == '__main__':
    st = dt_from_14digits_to_iso(20170920182730)
    ed = dt_from_14digits_to_iso(20170920183730)
    db.modpfvinfo.remove({"datetime":{"$gte":st,"$lte":ed}})
    db.modpfvmacinfo.remove({"datetime":{"$gte":st,"$lte":ed}})
    # st = dt_from_14digits_to_iso(20170905182730)
    # ed = dt_from_14digits_to_iso(20170907183730)
    remake_data(st,ed)
