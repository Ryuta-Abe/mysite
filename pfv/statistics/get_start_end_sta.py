# -*- coding: utf-8 -*-
from save_pfvinfo_sta import *
from convert_ip import convert_ip
from convert_nodeid import convert_nodeid
from convert_datetime import shift_seconds
from classify import classify
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale
from datetime import datetime, timedelta
from collections import Counter

client = MongoClient()
db = client.nm4bd
db.tmpcol.create_index([("_id.get_time_no", ASCENDING), ("_id.mac", ASCENDING)])

# CONST
# ノード番号の最大・最小を定義(init_nodecnt_dict()で使用)
MIN_NODE_NUM = 1
MAX_NODE_NUM = 27
# 測位対象フロアのリスト
FLOOR_LIST   = ["W2-6F","W2-7F","W2-9F"]
# 同一macの過去データ保持時間
int_time_range = 30
time_range = timedelta(seconds=int_time_range) # 過去の参照時間幅設定
# RSSIの閾値（機械学習使用時は機能しない）
TH_RSSI    = -70
# time_range以内の繰り返し出現回数
repeat_cnt = 99
# データ欠落時に滞留として端末を滞留させておく時間
INT_KEEP_ALIVE = 15
KEEP_ALIVE = timedelta(seconds=INT_KEEP_ALIVE)
# 分岐点で止める機能
INTERSECTION_FUNCTION = True
# 分岐点で止めたあとに5sec stayさせる機能(上がTrueのときのみ利用可)
STAY_AFTER_INTERSECTION = False
# 更新時間
min_interval = 5

# use Machine-Learning
USE_ML = False

def get_start_end_mod(all_st_time):
    """
    開始・終了の時刻・地点を決定するモジュール
    @param  all_st_time : datetime 開始時刻
    """
    from datetime import datetime, timedelta

    # 初期設定
    tmp_startdt = datetime(2000, 1, 1, 0, 0, 0)
    data_lists = [] #list for flow data
    data_lists_stay = [] #list for stay data
    nodecnt_dict = init_nodecnt_dict() #nodecnt_dictの初期化

    # data取り出し(from tmpcol)
    # タグのみ
    # datas = db.tmpcol.find({"_id.mac":{"$regex":"00:11:81:10:01:"}}).sort([("_id.mac",ASCENDING),("_id.get_time_no",ASCENDING)])
    # 全体
    datas = db.tmpcol.find().sort([("_id.mac",ASCENDING),("_id.get_time_no",ASCENDING)])
    make_pastmaclist() #pastdataからmacのみ抽出してpastmaclistを作成
    print("--- "+str(all_st_time)+" ---")

    if (datas.count() != 0):
        # 1番目の設定
        datas[0]["nodelist"] = reverse_list(datas[0]["nodelist"], "dbm")
        for data in datas: #macごとにループ
            ins_flag = False
            intersection_flag = False
            data["nodelist"] = reverse_list(data["nodelist"], "dbm") #dbm順にnodelistをソート

            data["id"] = data["_id"]
            del(data["_id"])

            # 過去の参照用データ　pastdata取り出し query:mac
            pastd = [] # 過去データ格納用
            pastd += db.pastdata.find({"mac":data["id"]["mac"]}) # 該当macの過去データを取り出す
            if (pastd != []) and (pastd[0]["pastlist"] != []):
                past_floor = pastd[0]["pastlist"][-1]["start_node"]["floor"]
            else:
                past_floor = None

            # nodelistデータ(floor,pcwl_id,rssi) reform
            # nodelistのデータを加工（{"ip":"XX.XX.XX.XX","dbm":○○} → {"floor":"XXXX","rssi":○○,"pcwl_id":○○}）
            for list_data in data["nodelist"][:]:
                list_data["floor"]   = convert_ip(list_data["ip"])["floor"]
                list_data["pcwl_id"] = convert_ip(list_data["ip"])["pcwl_id"]
                list_data["rssi"] = list_data["dbm"]
                del(list_data["ip"])
                del(list_data["dbm"])
                # floor error(階が不明な場合はdictをnodelistから除去)
                if list_data["floor"] == "Unknown":
                    data["nodelist"].remove(list_data)

            missing_flag = False #　消滅判定するフラグ
            # RSSI最大のノードがあるfloorの必要データ作成
            for list_data in data["nodelist"][:]:
                largest_floor = list_data["floor"] #大きいrssiを観測したノード順に最大階を確定
                if largest_floor != past_floor:
                    if list_data["rssi"] <= TH_RSSI+10:
                        missing_flag = True
                        break
                    floor_key = lambda x:x["floor"]
                    floor_cnt = Counter(list(map(floor_key,data["nodelist"][:min(5,len(data["nodelist"]))]))).most_common(2)
                    if floor_cnt[0][0] == past_floor: # フロアの出現件数最多フロアが過去データのフロアと一致する場合
                        largest_floor = floor_cnt[0][0]
                        break
                if largest_floor != "Unknown":
                    break #正式なフロアが割り当てられたらbreak
            if missing_flag:
                continue

            floor_node_list = [] #largest_floorのノードidのリスト
            floor_node_col = db.pcwlnode.find({"floor":largest_floor}).sort("pcwl_id",ASCENDING)
            for node in floor_node_col:
                floor_node_list.append(node["pcwl_id"])
            floor_rssi_list = [-99] * len(floor_node_list) #機械学習用にrssiのリストを作成（例：[-99,-99,・・・,・・・,・・・,-99]）


            for list_data in data["nodelist"][:]:
                # RSSIが最大のfloorのデータか否かで分岐
                if list_data["floor"] == largest_floor: # 最大の階か
                    if list_data["pcwl_id"] in floor_node_list: # その階にidが存在しているか
                        index = floor_node_list.index(list_data["pcwl_id"])
                        floor_rssi_list[index] = list_data["rssi"] # rssiのリストを更新（[-99,・・・,○,・・・,-99]）

            # 機械学習を使う場合
            if USE_ML and largest_floor != "Unknown":
                # 機械学習による分類を実行
                desc_index = classify(largest_floor, floor_rssi_list) # rssiのパターンから最近隣の可能性の高いノードのidの順位のリストを返す
                db.check_classify.insert({"rssi_list":floor_rssi_list,"floor":largest_floor,"rank_node":str(desc_index[0]),"len_node":len(data["nodelist"])})
                tmp_list = []
                for x in range(0,3): # 順位のリストより上位3つを抽出
                    predict_dict = {"floor":largest_floor, "pcwl_id":floor_node_list[desc_index[x]], "rssi":-60-x*10} # rssiの値を1位:-60,2位:-70,3位:-80としておく
                    tmp_list.append(predict_dict)
                data["nodelist"] = tmp_list # nodelistの中身を上位3つに置き換える
            else:
                tmp_list = []
                for list_data in data["nodelist"]: # 最大フロアのデータ上位3つを抽出
                    if (pastd != []) and ((len(tmp_list) == 1) or (len(tmp_list) == 2)) and (list_data["rssi"] == tmp_list[0]["rssi"]):
                        past_rank = pastd[0]["pastlist"][-1]["node"]
                        if (past_rank != []) and (past_rank[0]["floor"] == largest_floor):
                            for rank in past_rank:
                                if rank["pcwl_id"] == tmp_list[0]["pcwl_id"]:
                                    tmp_list.append(list_data)
                                    break
                                elif rank["pcwl_id"] == tmp_list[0]["pcwl_id"]:
                                    tmp_list.insert(0,list_data)
                                    break
                                else:
                                    pass
                    elif (list_data["floor"] == largest_floor):
                        tmp_list.append(list_data)
                    if (list_data["floor"] == largest_floor) and (tmp_list[-1]["pcwl_id"] != list_data["pcwl_id"]):
                        tmp_list.append(list_data)
                    if len(tmp_list) == 3:
                        break
                data["nodelist"] = tmp_list # nodelistの中身を上位3つに置き換える

            # RSSI上位3つまで参照
            node_cnt = min(len(data["nodelist"]), 3)

            # update_dtを下回る以上データがいるか確認
            if (pastd != []) and (data["id"]["get_time_no"] <= pastd[0]["update_dt"]):
                print("0:(dt > update_dt)or(pastd==[])")
                pass
            else:
                # 無ければ初期nodecnt_dict, 初期pastlistを作成
                if pastd == []: # 過去データが存在しない場合
                    tmp_dict = {"mac":data["id"]["mac"], "nodecnt_dict":init_nodecnt_dict(), "pastlist":[], "update_dt":data["id"]["get_time_no"]}
                    pastd.append(tmp_dict) # 初期データを作成し過去データ用のリストに追加

                tmp_enddt = data["id"]["get_time_no"] # 解析対象時刻を一時的な終了時刻とする
                pastlist = pastd[0]["pastlist"]
                # pastdata確認
                if (pastlist != []):
                    # pastlist1件ずつ参照
                    make_nodecnt_dict(pastlist, data["id"]["get_time_no"], pastd[0]["nodecnt_dict"]) # time_range外のデータとカウントを除去

                    pastlist = reverse_list(pastlist, "dt")

                update_nodecnt_dict(node_cnt, min_interval ,data, pastd[0]["nodecnt_dict"]) # 最近隣候補のノードのカウントを増やす
                if (pastlist != []):
                    pastlist = reverse_list(pastlist, "dt") # 過去データを新しい順にソート
                    tmp_startdt = pastlist[0]["dt"] # 最新の過去データを一時的な開始時刻とする

                    # stay after intersection（分岐の次のデータを滞留扱いとする処理）
                    if (STAY_AFTER_INTERSECTION and pastlist[0]["arrive_intersection"]):
                        se_data = append_data_lists_stay_alt(data["id"]["mac"], tmp_startdt, tmp_enddt, pastlist[0]["start_node"], data_lists_stay)
                        # print(se_data)
                        data_lists_stay.append(se_data)
                        update_pastlist_alt(pastd[0], tmp_enddt, 0, data["nodelist"], pastlist[0]["start_node"]) # 現在のデータを過去データに追加
                        save_pastd(pastd[0], tmp_enddt) # 元の過去データをDBから除去し、新たな過去データを保存
                        ins_flag = True

                    else:
                        # node loop (sorted by RSSI)
                        for num in range(0, node_cnt): # 上位3つの候補順にループ
                            tmp_node   = data["nodelist"][num]
                            tmp_id_str = str(tmp_node["pcwl_id"])
                            tmp_floor  = tmp_node["floor"]

                            if tmp_floor == "Unknown":
                                continue # フロアが正常でない場合は処理を中断し次の候補へ
                            if (tmp_node["rssi"] >= TH_RSSI): # 閾値判定
                                # flow（移動データの場合）
                                # 現在の候補のノードと過去データにおける出発ノードが異なるかつフロアが同一である場合
                                if (tmp_node["pcwl_id"] != pastlist[0]["start_node"]["pcwl_id"])and(tmp_floor == pastlist[0]["start_node"]["floor"]):
                                    # print("flow")
                                    if (pastd[0]["nodecnt_dict"][tmp_floor][tmp_id_str] <= repeat_cnt): # 過去データの該当ノードのカウント数がカウント上限以内の場合
                                        interval = (tmp_enddt - tmp_startdt).seconds # 現在の時刻と過去で他の時刻差
                                        d_total = get_min_distance(tmp_floor, pastlist[0]["start_node"]["pcwl_id"], tmp_node["pcwl_id"]) # 開始ノードと終了ノード間の距離を計算

                                        # intervalに応じて距離フィルタを可変に
                                        velocity = fix_velocity(tmp_floor, interval) # intervalに応じた速度を得る
                                        if d_total < interval * velocity: # 移動距離が規定距離以内の場合

                                            past_ed_node = [pastlist[0]["start_node"]] # データ構造[{"pcwl_id","rssi","floor"}]
                                            current_node = [tmp_node]                  # データ構造[{"pcwl_id","rssi","floor"}]
                                            past_ed_id   = past_ed_node[0]["pcwl_id"]
                                            current_id   = current_node[0]["pcwl_id"]
                                            current_st_ed= [past_ed_id, current_id] # ノード間の移動情報
                                            route_info = []
                                            route_info += db.pcwlroute.find({"$and":[{"floor" : tmp_floor},
                                                                                    {"query" : current_st_ed[0]},
                                                                                    {"query" : current_st_ed[1]}]}) # 移動する経路の経路情報を取り出し

                                            # 向きの最適化と各経路の重み付けを行う（save_pfvinfo.py内の関数）
                                            route_info = optimize_routeinfo(past_ed_node, current_node, route_info[0]["dlist"])
                                            if len(route_info) >= 2:
                                                route_info = select_one_route(route_info) # addが最大の1つの経路のみ取り出す

                                            # 行き来をstayに（往復除去フィルター）
                                            len_pastlist = len(pastlist) # 最大:time_range/min_intervalの値をとる
                                            if (len_pastlist >= 2): # 過去のデータが2件以上ある場合
                                                past_st_node = [pastlist[1]["start_node"]] # 1つ前のデータの出発点
                                                past_st_id   = past_st_node[0]["pcwl_id"]

                                                ### TODO:経路部分一致でstayに ###
                                                current_route = [] # 現時刻の移動経路
                                                for route in route_info[0]["route"]:
                                                    current_route.append(route["direction"])

                                                q_lt  = data["id"]["get_time_no"] # 現在の時刻
                                                q_gte = shift_seconds(q_lt, - min_interval) # 現在の時刻からmin_interval分前の時刻
                                                past_route = [] # 1つ前の時刻の経路
                                                past_route += db.pfvmacinfo.find({"mac":data["id"]["mac"], "datetime":{"$gte":q_gte,"$lt":q_lt}}).sort("datetime",-1)
                                                if (len(past_route) == 1):
                                                    # print(current_route, past_route[0]["route"])

                                                    if (route_partial_match(current_route, past_route[0]["route"])): # True：一致で滞留判定、False：不一致
                                                        # data_lists_"stay" append
                                                        data_lists_stay.append(append_data_lists_stay_alt(data["id"]["mac"], tmp_startdt, tmp_enddt, pastlist[0]["start_node"], data_lists_stay))
                                                        # print("alt_stay")
                                                        # pastlist update
                                                        update_pastlist_alt(pastd[0], tmp_enddt, num, data["nodelist"], pastlist[0]["start_node"]) # 現在のデータを過去データに追加
                                                        save_pastd(pastd[0], tmp_enddt) # 元の過去データ除去し、新たな過去データを保存
                                                        ins_flag = True
                                                        break

                                            # stop once at intersection（分岐ノードを終了ノードと判定とする）
                                            if INTERSECTION_FUNCTION and (interval == 5):
                                                for route in route_info[0]["route"]: # 移動する全経路のうちそれぞれの経路の終点側のノードで判定を行う
                                                    after_node_id = route["direction"][1]
                                                    after_node_info = db.pcwlnode.find_one({"floor":tmp_floor,"pcwl_id":after_node_id})
                                                    if (len(after_node_info["next_id"])>=3): # 隣接するノードが3つ以上の場合
                                                        intersection_flag = True # 分岐点判定
                                                        break

                                                if intersection_flag: # 分岐点の場合
                                                    # data_lists append
                                                    del(after_node_info["pos_x"],after_node_info["pos_y"],after_node_info["_id"],after_node_info["next_id"]) # afternode_info:{"pcwl_id":,"floor":}
                                                    after_node_info["rssi"] = None
                                                    se_data = append_data_lists(num, data, tmp_startdt, tmp_enddt, pastlist[0]["start_node"], data_lists)
                                                    if se_data != None:
                                                        se_data["end_node"] = [{"floor":tmp_floor,"pcwl_id":after_node_id,"rssi":None}] # 終了ノードを分岐ノードに置き換える
                                                        data_lists.append(se_data)
                                                        # pastlist update
                                                        update_pastlist_intersection(pastd[0], tmp_enddt, num, data["nodelist"], after_node_info)
                                                    save_pastd(pastd[0], tmp_enddt)
                                                    # print("======================================")
                                                    ins_flag = True
                                                    break

                                            # data_lists append（ノーマルな移動情報）
                                            node_info = db.pcwlnode.find_one({"floor":tmp_floor, "pcwl_id":current_id})

                                            if (len(node_info["next_id"])>=3): # 移動の最終ノードが分岐（隣接3つ以上）の場合
                                                # print("===== at intersection =====")
                                                data_lists.append(append_data_lists(num, data, tmp_startdt, tmp_enddt, pastlist[0]["start_node"], data_lists))
                                                # pastlist update
                                                update_pastlist_intersection(pastd[0], tmp_enddt, num, data["nodelist"], tmp_node) # 分起終着として過去データを更新
                                                # print(pastd[0])
                                            else:
                                                # print("================")
                                                data_lists.append(append_data_lists(num, data, tmp_startdt, tmp_enddt, pastlist[0]["start_node"], data_lists))
                                                # pastlist update
                                                update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"]) # 過去データを更新
                                                # print(pastd[0])

                                            save_pastd(pastd[0], tmp_enddt) # 元の過去データをDBより消去し、新たな過去データを保存
                                            # print("flow1")
                                            ins_flag = True
                                            break

                                    else: # 過去データのノードのカウントがカウント制限を超えている場合
                                        # pastlist update
                                        update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"])
                                        save_pastd(pastd[0], tmp_enddt)
                                        print("over repeat_cnt")
                                        ins_flag = True
                                        break

                                # stay（滞留データの場合）
                                # 現在の候補のノードと出発点が同じであるかつ同一フロアである場合
                                elif (tmp_node["pcwl_id"] == pastlist[0]["start_node"]["pcwl_id"])and(tmp_floor == pastlist[0]["start_node"]["floor"]):
                                    # print("stay")
                                    if (pastd[0]["nodecnt_dict"][tmp_floor][tmp_id_str] <= repeat_cnt): # カウント制限以内である場合
                                        # data_lists_stay append
                                        data_lists_stay.append(append_data_lists_stay(num, data, tmp_startdt, tmp_enddt, tmp_node, data_lists_stay))
                                        # pastlist update
                                        update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"])
                                        save_pastd(pastd[0], tmp_enddt)
                                        # print("stay1")
                                        ins_flag = True
                                        break
                                    else: # カウント制限を超えた場合
                                        update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"])
                                        save_pastd(pastd[0], tmp_enddt)
                                        # print("stay2")
                                        ins_flag = True
                                        break
                                # other floor（候補の会と出発点の階が異なる場合）
                                else:
                                    # print("4:other floor")
                                    # pastlist update
                                    update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"])
                                    save_pastd(pastd[0], tmp_enddt)
                                    ins_flag = True
                                    break

                            # RSSI小
                            else:
                                # print("5:low RSSI")
                                break

                # pastlist == [] (time_range内の過去データが存在しない)の場合
                else:
                    # print("6:not append")
                    for num in range(0, node_cnt):
                        tmp_node   = data["nodelist"][num]
                        if (tmp_node["rssi"] >= TH_RSSI): # rssiの閾値判定
                            # nodecnt_dict update
                            # pastlist update
                            update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"]) # 現在のデータを過去データに追加
                            save_pastd(pastd[0], tmp_enddt) # 元の過去データをDBより消去し、新たな過去データを保存
                            ins_flag = True
                            break

            if (ins_flag):
                update_maclist(data["id"]["mac"]) # pastmaclistから正常に処理が行われたmacを取り除く

        # data_lists      = reverse_list(data_lists, "start_time")
        # data_lists_stay = reverse_list(data_lists_stay, "start_time")

    # pastdata check　/ dataが取れなかった場合一旦stay
    past_maclist = db.pastmaclist.find() # 正常に処理が行われなかったmac。データの取れなかったmacが残っている
    for data in past_maclist:
        mac = data["_id"]["mac"] # 該当のmacを格納
        pastmacdata = db.pastdata.find_one({"mac":mac}) # 該当のmacに関する過去データを取得
        pastmacdata["pastlist"] = reverse_list(pastmacdata["pastlist"], "dt") # 過去データを時系列順にソート
        # print(pastmacdata)

        make_nodecnt_dict(pastmacdata["pastlist"], all_st_time, pastmacdata["nodecnt_dict"]) # time_range外のカウント過去データを除去
        if (len(pastmacdata["pastlist"]) != 0):
            for node in pastmacdata["pastlist"]:
                if(all_st_time - node["dt"] <= KEEP_ALIVE): # 過去データとの時刻差以内の場合
                    if (node["alive"]):
                        # print(node)
                        data_lists_stay.append(append_data_lists_stay_alt(mac, shift_seconds(all_st_time, -5), all_st_time, node["start_node"], data_lists_stay))
                        update_pastlist_keep_alive(pastmacdata, all_st_time, 0, [], node["start_node"]) # "alive"：Falseで過去データを追加
                        # print("keep alive stay")
                        save_pastd(pastmacdata, all_st_time) # DB内の過去データを更新
                        break

    # save_pfvinfo.py へ渡す
    make_pfvinfo(data_lists,db.pfvinfo,min_interval)
    make_stayinfo(data_lists_stay,db.stayinfo,min_interval)
    make_pfvmacinfo(data_lists,db.pfvmacinfo,min_interval)
    make_staymacinfo(data_lists_stay,db.staymacinfo,min_interval)

def get_min_distance(floor, node1, node2):
    """
    2AP間の最小距離を返す関数
    @param  floor:str
    @param  node1:int
    @param  node2:int
    @return d_total:float
    pcwlroute:{ "_id" : ObjectId("5858e9070a3b117be5b29537"), "query" : [ 9, 8 ], "dlist" : [ [ { "direction" : [ 9, 25 ], "distance" : 100 }, { "direction" : [ 25, 8 ], "distance" : 70 } ] ], "floor" : "W2-7F" }
    """
    d_total = 0
    # 経路情報の取り出し
    route_info = []
    route_info += db.pcwlroute.find({"$and":[{"floor":floor},{"query":node1},{"query":node2}]})
    # 最小距離算出
    for info in route_info:
        for route in info["dlist"]:
            tmp_d_total = 0
            for part in route:
                tmp_d_total += part["distance"]
            if d_total == 0:
                d_total = tmp_d_total
            if (tmp_d_total < d_total):
                d_total = tmp_d_total

    return d_total

def init_nodecnt_dict():
    """
    nodecnt_dictの初期化
    @return nodecnt_dict:dict
        (ex: {"W2-6F":{1:0,2:0,...},...})
    """
    nodecnt_dict = {}
    for floor in FLOOR_LIST:
        nodecnt_dict.update({floor:{}})
        for num in range(MIN_NODE_NUM, MAX_NODE_NUM+1):
            nodecnt_dict[floor].update({str(num):0})

    return nodecnt_dict

def make_nodecnt_dict(node_history, get_time_no, nodecnt_dict):
    """
    nodecnt_dictを更新
    (過去のデータ[node_history]から、過去1分間に入っていないデータ分のカウントを減らす)
    @param:node_hisory[ { "dt" : ISODate("2017-07-14T14:26:10Z"), "alive" : false, "node" : [ ], "start_node" : { "pcwl_id" : 7, "floor" : "W2-9F", "rssi" : -60 }, "arrive_intersection" : false },・・・ ]
    @param:解析対象時刻
    @param:過去データのノードのカウント情報
    """
    for history in node_history[:]: # time_range分の過去データでループ
        his_node_cnt = min(len(history["node"]),3)
        if not(get_time_no - time_range <= history["dt"] <= get_time_no): # 過去データが解析対象時刻よりtime_range秒前までのデータではない場合
            for h_num in range(0, his_node_cnt): # 必要回数分nodecnt_dictのカウントを減らす
                tmp_id   = history["node"][h_num]["pcwl_id"]
                tmp_floor = history["node"][h_num]["floor"]
                nodecnt_dict[tmp_floor].update({str(tmp_id) : nodecnt_dict[tmp_floor][str(tmp_id)]-1})
                if nodecnt_dict[tmp_floor][str(tmp_id)] == -1:
                    print("---------! nodecnt_dict -1 error !---------")
                    pass
            node_history.remove(history) # 過去データからtime_range外のデータを除去

def update_nodecnt_dict(node_cnt, min_interval, data, nodecnt_dict):
    """
    nodecnt_dictを更新
    (最新時刻のデータ中に含まれるデータ分nodecnt_dictのカウントを増やす)
    """
    for num in range(0, node_cnt):
        tmp_id   = data["nodelist"][num]["pcwl_id"]
        tmp_floor = data["nodelist"][num]["floor"]
        nodecnt_dict[tmp_floor].update({str(tmp_id) : nodecnt_dict[tmp_floor][str(tmp_id)]+1})
        if nodecnt_dict[tmp_floor][str(tmp_id)] > int_time_range / min_interval + 1:
            print("---------! nodecnt_dict > 7 error !---------")
            pass

def append_data_lists(num, data, tmp_startdt, tmp_enddt, tmp_node_id, data_lists):
    """
    data_lists(移動データ保存リスト)にse_data[Start and End data]を追加するために
    se_dataを作成する関数
    @return se_data:dict
    """
    if tmp_enddt < tmp_startdt:
        print("---------! ed > st error !---------")
    if (tmp_enddt - tmp_startdt).seconds > int_time_range:
        print("---------! flow ed-st>60 error !---------")
    if (tmp_enddt - tmp_startdt).seconds > min_interval:
        return None
    se_data =  {"mac":data["id"]["mac"],
                "start_time":tmp_startdt,
                "end_time"  :tmp_enddt,
                "interval"  :(tmp_enddt - tmp_startdt).seconds,
                "start_node":[tmp_node_id],
                "end_node"  :[data["nodelist"][num]],
                "floor"     :tmp_node_id["floor"],
                }
    return se_data

def append_data_lists_stay(num, data, tmp_startdt, tmp_enddt, tmp_node_id, data_lists_stay):
    """
    data_lists_stay(静止データ保存リスト)にse_data[Start and End data]を追加するために
    se_dataを作成する関数
    @return se_data:dict
    """
    if tmp_enddt < tmp_startdt:
        print("---------! ed > st error !---------")
    if (tmp_enddt - tmp_startdt).seconds > int_time_range:
        print("---------! stay ed-st>60 error !---------")
    if (tmp_enddt - tmp_startdt).seconds > min_interval:
        return None
    se_data =  {"mac":data["id"]["mac"],
                "start_time":tmp_startdt,
                "end_time"  :tmp_enddt,
                "interval"  :(tmp_enddt - tmp_startdt).seconds,
                "start_node":tmp_node_id["pcwl_id"],
                "end_node"  :data["nodelist"][num]["pcwl_id"],
                "floor"     :tmp_node_id["floor"],
                }
    return se_data

def append_data_lists_stay_alt(mac, tmp_startdt, tmp_enddt, tmp_node_id, data_lists_stay):
    """
    data_lists(移動データ保存リスト)にse_data[Start and End data]を追加するために
    se_dataを作成する関数
    [行き来した場合をstayにするときに使用]
    @return se_data:dict
    """
    if tmp_enddt < tmp_startdt:
        print("---------! ed > st error !---------")
    if (tmp_enddt - tmp_startdt).seconds > int_time_range:
        print("---------! stay ed-st>60 error !---------")
    if (tmp_enddt - tmp_startdt).seconds > min_interval:
        return None
    se_data =  {"mac":mac,
                "start_time":tmp_startdt,
                "end_time"  :tmp_enddt,
                "interval"  :(tmp_enddt - tmp_startdt).seconds,
                "start_node":tmp_node_id["pcwl_id"],
                "end_node"  :tmp_node_id["pcwl_id"],
                "floor"     :tmp_node_id["floor"],
                }
    return se_data

# pastlistの更新用関数
def update_pastlist(pastd, get_time_no, num, nodelist):
    past_dict = {"dt":get_time_no, "start_node":nodelist[num], "node":nodelist, "alive":True, "arrive_intersection":False}
    pastd["pastlist"].append(past_dict)

def update_pastlist_intersection(pastd, get_time_no, num, nodelist, start_node):
    past_dict = {"dt":get_time_no, "start_node":start_node, "node":nodelist, "alive":True, "arrive_intersection":True}
    pastd["pastlist"].append(past_dict)

# 逆経路と部分一致 or 分岐点到着後のstay用
def update_pastlist_alt(pastd, get_time_no, num, nodelist, start_node):
    past_dict = {"dt":get_time_no, "start_node":start_node, "node":nodelist, "alive":True, "arrive_intersection":False}
    pastd["pastlist"].append(past_dict)

# データ欠落時、一旦stayで残しておく用
def update_pastlist_keep_alive(pastd, get_time_no, num, nodelist, start_node):
    past_dict = {"dt":get_time_no, "start_node":start_node, "node":nodelist, "alive":False, "arrive_intersection":False}
    pastd["pastlist"].append(past_dict)

def save_pastd(pastd,update_dt):
    """
    pastd(過去データ)更新用
    各macに対する最終更新時刻を保存しておく
    @param  pastd:dict
    @param  update_dt:datetime
    """
    pastd = {"mac":pastd["mac"],
             "update_dt":update_dt,
             "nodecnt_dict":pastd["nodecnt_dict"],
             "pastlist":pastd["pastlist"],
            }
    db.pastdata.remove({"mac":pastd["mac"]})
    db.pastdata.save(pastd)

def fix_velocity(floor, interval):
    """
    各フロアでの移動速度制限を設定
    110[px] = 14.4[m] に相当
    5sec or 10sec over で分けているが、現状5secしか機能していない...
    6,7,9Fに関しては170px/5secが最大なので、v_W2_nF = 17 としておけばよい(マージンも要るか...)
    @param  floor:str
    @param  interval:int
    @return velocity:float
    """
    v_W2_6F = 30
    v_W2_7F = 30
    v_W2_8F = 30
    v_W2_9F = 30
    v_kaiyo = 62
    velocity_dict = {"W2-6F":{"lt10":v_W2_6F*2,"gte10":v_W2_6F},
                     "W2-7F":{"lt10":v_W2_7F*2,"gte10":v_W2_7F},
                     "W2-8F":{"lt10":v_W2_8F*2,"gte10":v_W2_8F},
                     "W2-9F":{"lt10":v_W2_9F*2,"gte10":v_W2_9F},
                     "kaiyo":{"lt10":v_kaiyo*2,"gte10":v_kaiyo},
                    }
    if interval < 10:
        velocity = velocity_dict[floor]["lt10"]
    else:
        velocity = velocity_dict[floor]["gte10"]
    return velocity

def route_partial_match(current_route, past_route):
    """
    逆経路と部分一致しているかの判定をする関数
    @param  current_route:list
    @param  past_route:list
    @return stay_flag:Boolean
    """
    current_len = len(current_route)
    past_len    = len(past_route)
    if (current_len <= past_len):
        past_route.reverse()
        # print(past_route)
        for num in range(0,current_len):
            past_route[num].reverse()
            # print(past_route[num], current_route[num])
            if (past_route[num] == current_route[num]):
                stay_flag = True
            else:
                stay_flag = False
                break

    else:
        stay_flag = False
    return stay_flag

def reverse_list(data_list, sort_key):
    """
    特定のkeyに関して、listを逆順にする関数
    @param  data_list:list
    @param  sort_key:str
    @return data_list:list
    """
    data_list = sorted(data_list, key=lambda x:x[str(sort_key)], reverse=True)
    return data_list

def make_pastmaclist():
    """
    pastdataコレクションから過去データ(1min)に含まれるmacアドレスを抽出した
    pastmaclistコレクションを作成する
    """
    db.pastdata.aggregate([
                            {"$group":
                                {"_id":
                                    {"mac":"$mac"},
                                },
                            },
                            {"$out": "pastmaclist"},
                        ],
                        allowDiskUse=True,
                    )

def update_maclist(mac):
    """
    pastmaclistから現在参照している時刻のデータに含まれる
    macアドレスと一致するものを除外する
    @param  mac:str
    """
    if (db.pastmaclist.find({"_id.mac":mac}).count() == 1):
        db.pastmaclist.remove({"_id.mac":mac})
