# -*- coding: utf-8 -*-
from save_pfvinfo import *
from convert_ip import convert_ip
from convert_nodeid import convert_nodeid
from convert_datetime import shift_seconds
from classify import classify
from pymongo import *

import json, math, datetime, locale
from datetime import datetime, timedelta

client = MongoClient()
db = client.nm4bd
db.tmpcol.create_index([("_id.get_time_no", ASCENDING), ("_id.mac", ASCENDING)])

# CONST
MIN_NODE_NUM = 1
MAX_NODE_NUM = 27
FLOOR_LIST   = ["W2-6F","W2-7F","W2-8F","W2-9F","kaiyo"]
int_time_range = 30
time_range = timedelta(seconds=int_time_range) # 過去の参照時間幅設定
TH_RSSI    = -80
repeat_cnt = 99
INT_KEEP_ALIVE = 15
KEEP_ALIVE = timedelta(seconds=INT_KEEP_ALIVE)
MAC_HEAD = "00:11:81:10:01:"
# 分岐点で止める機能
INTERSECTION_FUNCTION = True
# 分岐点で止めたあとに5sec stayさせる機能(上がTrueのときのみ利用可)
STAY_AFTER_INTERSECTION = False
min_interval = 5  # PRデータの取得間隔

# True when use Machine-Learning
USE_ML = True

def get_start_end(st):
    """
    開始・終了の時刻・地点を決定
    @param  st : datetime 開始時刻
    """

    # 希望ののPRデータのみ抽出
    pr_pr_data_list = db.tmpcol.find({"_id.mac":{"$regex":MAC_HEAD}}).sort([("_id.mac",ASCENDING),("_id.get_time_no",ASCENDING)])

    if(len(pr_pr_data_list == 0)):
        for pr_pr_data in pr_pr_data_list:
            # node_listをdbmの降順に(大きなものから)並べなおす
            pr_pr_data["node_list"] = reverse_list(pr_pr_data["node_list"],"dbm")

            # RSSI最大のノードがあるfloorの必要データ作成
            for node in node_list:
                largest_floor = convert_ip(node["ip"])["floor"]
                if largest_floor != "Unknown":
                    break
            floor_node_list = []  # pcwl_idはとびとびの値であるから、[1,2,3,5,7]のようなpcwl_idを昇順に並べたリスト
            floor_node_col = db.pcwlnode.find({"floor":largest_floor}).sort("pcwl_id",ASCENDING)
            for node in floor_node_col:
                floor_node_list.append(node["pcwl_id"])
            floor_rssi_list = [-99] * len(floor_node_list)
            
            # nodelistデータ({"floor","pcwl_id","rssi"}) reform, tmpcol_backupに保存
            for list_pr_data in pr_pr_data["nodelist"][:]:
                list_pr_data["floor"]   = convert_ip(list_pr_data["ip"])["floor"]
                list_pr_data["pcwl_id"] = convert_ip(list_pr_data["ip"])["pcwl_id"]
                list_pr_data["rssi"] = list_pr_data["dbm"]
                del(list_pr_data["ip"])
                del(list_pr_data["dbm"])
                # floor error
                if list_pr_data["floor"] == "Unknown":
                    pr_pr_data["nodelist"].remove(list_pr_data)

                # RSSIが最大のfloorのデータか否かで分岐
                if list_pr_data["floor"] == largest_floor:
                    if list_pr_data["pcwl_id"] in floor_node_list:
                        index = floor_node_list.index(list_pr_data["pcwl_id"])
                        floor_rssi_list[index] = list_pr_data["rssi"]            
            pr_pr_data["id"] = pr_pr_data["_id"]
            del(pr_pr_data["_id"])
            db.tmpcol_backup.insert(pr_data)

            get_analyzed_pos(pr_pr_data,floor_rssi_list)

    else:

def get_analyzed_pos(pr_data,rssi_list):
    # RSSI上位3つまでPRデータを参照するため、ノード数node_cnt(3以下)を算出
    node_cnt = min(len(pr_data["nodelist"]), 3)
    nodelist = pr_data["nodelist"]
    dt = pr_data["id"]["get_time_no"]

    flow_list = []
    stay_list = []

    if USE_ML and largest_floor != "Unknown":
        desc_index, classes = classify(largest_floor, rssi_list)
        predicted_nodelist = []
        for i in range(0,3):
            label = clf.classes[desc_indexes[i]]
            if "," in label:
                position_str = desc_index[i]
                position = list(label.split("[")[1].split("]")[0].split(","))
            else:
                predict_dict = {"floor":largest_floor, "pcwl_id":floor_node_list[desc_index[i]], "rssi":-60-i*10}
            predicted_nodelist.append(predict_dict)
        # 判定されたノード候補を表示
        # print("1st : "+str(floor_node_list[desc_index[0]]))
        # print("2nd : "+str(floor_node_list[desc_index[1]]))
        # print("3rd : "+str(floor_node_list[desc_index[2]]))
        nodelist = predicted_nodelist
    
    # 過去の参照用データ　pastdata取り出し query:mac
    pastd = db.pastdata.find_one({"mac":pr_data["id"]["mac"]})

    # update_dtを下回る以上データがいるか確認
    if (pastd != []) and (dt <= pastd[0]["update_dt"]):
        print("0:(pr_dt < update_dt)or(pastd==[])")
        return -1
    # 無ければ初期nodecnt_dict, 初期pastlistを作成
    if pastd is None:
        tmp_dict = {"mac":mac, "nodecnt_dict":init_nodecnt_dict(), "pastlist":[], "update_dt":pr_data["id"]["get_time_no"]}
        pastd.append(tmp_dict)
    
    pastlist = pastd["pastlist"]
    # pastdata確認
    if (pastlist != []):
        # 1. pastlistを1件ずつ参照し、過去30秒間に入っていないデータ分のカウントを減らす
        make_nodecnt_dict(pastlist, dt, pastd["nodecnt_dict"])
        pastlist = reverse_list(pastlist, "dt")

    # 2. 最新時刻のデータ中に含まれるデータ分nodecnt_dictのカウントを増やす
    update_nodecnt_dict(node_cnt, min_interval ,pr_data, pastd["nodecnt_dict"])

    if(pastd != []):
        start_dt = pastd["update_dt"]
        if (STAY_AFTER_INTERSECTION and pastlist[0]["arrive_intersection"]):
            se_data = make_stay_list(mac, start_dt, dt, pastlist["start_node"], data_lists_stay)
            stay_list.append(se_data)
            update_pastlist_alt(pastd[0], tmp_enddt, 0, data["nodelist"], pastlist["start_node"])
            save_pastd(pastd[0], tmp_enddt)
            ins_flag = True


# def stay_after_intersection():
#     se_data = append_data_lists_stay_alt(data["id"]["mac"], tmp_startdt, tmp_enddt, pastlist[0]["start_node"], stay_lists)
#     # print(se_data)
#     data_lists_stay.append(se_data)
#     update_pastlist_alt(pastd[0], tmp_enddt, 0, data["nodelist"], pastlist[0]["start_node"])
#     save_pastd(pastd[0], tmp_enddt)
#     ins_flag = True



    

def make_stay_list(mac,st_dt,ed_dt,node_id,)
    """
    data_lists(移動データ保存リスト)にse_data[Start and End data]を追加するために
    se_dataを作成する関数
    [行き来した場合やデータが取れていない場合をstayにするときに使用]
    append_data_lists_stayとは引数が異なるが、機能は類似
    @oaram tmp_startdt: 最新過去データの取得時刻
    @param tmp_enddt: 取得データの時刻
    @oaram tmp_node_id: 最新過去データのノード情報(ex: "start_node" : {"floor" : "W2-6F","pcwl_id" : 14,"rssi" : -55})
    @return se_data:dict
    """
    if tmp_enddt < tmp_startdt:  #  error:取得データの時刻 < 最新過去データの時刻の場合
        print("---------! ed > st error !---------")
    if (tmp_enddt - tmp_startdt).seconds > int_time_range:  # error: 最新過去データの時刻より離れすぎている場合
        print("---------! stay ed-st>30 error !---------")
    if (tmp_enddt - tmp_startdt).seconds > min_interval:  # 取得データの時刻-最新過去データの時刻が取得間隔(5s)を超えている場合
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






