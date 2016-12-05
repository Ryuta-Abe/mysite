# -*- coding: utf-8 -*-
from save_pfvinfo import *
from convert_ip import convert_ip
from convert_nodeid import convert_nodeid
from convert_datetime import shift_seconds
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale
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

# TODO:add input : all start time
def get_start_end_mod(all_st_time):
    from datetime import datetime, timedelta
    # dt05
    min_interval = 5

    ### DEBUG用DB初期化 ##############
    DEBUG = False
    if (DEBUG):
        db.pastdata.drop()
        db.pfvinfo.drop()
        db.pfvmacinfo.drop()
        db.stayinfo.drop()
        db.staymacinfo.drop()
    #################################

    # 初期設定
    count     = 0
    count_all = 0
    tmp_mac   = ""
    tmp_startdt = datetime(2000, 1, 1, 0, 0, 0)
    data_lists = []
    data_lists_stay = []
    data_lists_experiment = []
    node_history = []
    start_nodelist = []
    end_node_list = []
    nodecnt_dict = init_nodecnt_dict()

    # data取り出し
    mac_query = ""
    # datas = db.tmpcol.find().sort([("_id.mac",ASCENDING),("_id.get_time_no",ASCENDING)])
    datas = db.tmpcol.find({"_id.mac":{"$regex":"00:11:81:10:01:"}}).sort([("_id.mac",ASCENDING),("_id.get_time_no",ASCENDING)])
    make_pastmaclist()
    # print("gse_count:"+str(datas.count()))
    # print("--- "+str(all_st_time)+" ---")

    if (datas.count() != 0):
        # 1番目の設定
        datas[0]["nodelist"] = reverse_list(datas[0]["nodelist"], "dbm")
        for data in datas:
            ins_flag = False
            intersection_flag = False
            
            remove_list = []
            loop_cnt = 0
            for list_data in data["nodelist"][:]:
                list_data["floor"]   = convert_ip(list_data["ip"])["floor"]
                list_data["pcwl_id"] = convert_ip(list_data["ip"])["pcwl_id"]
                list_data["rssi"] = list_data["dbm"]
                del(list_data["ip"])
                del(list_data["dbm"])
                if list_data["floor"] == "Unknown":
                    data["nodelist"].remove(list_data)
                loop_cnt += 1
            
            db.tmpcol_backup.insert(data)
            data["id"] = data["_id"]
            del(data["_id"])

            data["nodelist"] = reverse_list(data["nodelist"], "rssi")
            
            # RSSI上位3つまで参照
            node_cnt = min(len(data["nodelist"]), 3)

            # 過去の参照用データ　pastdata取り出し query:mac
            pastd = []
            pastd += db.pastdata.find({"mac":data["id"]["mac"]})
            
            if (pastd != []) and (data["id"]["get_time_no"] <= pastd[0]["update_dt"]):
                print("0:(dt > update_dt)or(pastd==[])")
                pass
            else:
                # 無ければ初期nodecnt_dict, 初期pastlistを作成
                if pastd == []:
                    tmp_dict = {"mac":data["id"]["mac"], "nodecnt_dict":init_nodecnt_dict(), "pastlist":[], "update_dt":data["id"]["get_time_no"]}
                    pastd.append(tmp_dict)

                tmp_enddt = data["id"]["get_time_no"]
                pastlist = pastd[0]["pastlist"]
                # pastdata確認
                if (pastlist != []):
                    # pastlist1件ずつ参照
                    make_nodecnt_dict(pastlist, data["id"]["get_time_no"], pastd[0]["nodecnt_dict"])

                    pastlist = reverse_list(pastlist, "dt")

                update_nodecnt_dict(node_cnt, min_interval ,data, pastd[0]["nodecnt_dict"])
                if (pastlist != []):
                    pastlist = reverse_list(pastlist, "dt")
                    tmp_startdt = pastlist[0]["dt"]

                    # node loop (sorted by RSSI)
                    for num in range(0, node_cnt):
                        tmp_node   = data["nodelist"][num]
                        tmp_id_str = str(tmp_node["pcwl_id"])
                        tmp_floor  = tmp_node["floor"]
                        if tmp_floor == "Unknown":
                            continue
                        if (tmp_node["rssi"] >= TH_RSSI):
                            # flow
                            if (tmp_node["pcwl_id"] != pastlist[0]["start_node"]["pcwl_id"])and(tmp_floor == pastlist[0]["start_node"]["floor"]):
                                # print("flow")
                                if (pastd[0]["nodecnt_dict"][tmp_floor][tmp_id_str] <= repeat_cnt):
                                    interval = (tmp_enddt - tmp_startdt).seconds
                                    d_total = get_min_distance(tmp_floor, pastlist[0]["start_node"]["pcwl_id"], tmp_node["pcwl_id"])

                                    # intervalに応じて距離フィルタを可変に
                                    velocity = fix_velocity(tmp_floor, interval)
                                    if d_total < interval * velocity:
                                        
                                        past_ed_node = [pastlist[0]["start_node"]]
                                        current_node = [tmp_node]
                                        past_ed_id   = past_ed_node[0]["pcwl_id"]
                                        current_id   = current_node[0]["pcwl_id"]
                                        current_st_ed= [past_ed_id, current_id]
                                        route_info = [] 
                                        route_info += db.pcwlroute.find({"$and":[{"floor" : tmp_floor},
                                                                                {"query" : current_st_ed[0]}, 
                                                                                {"query" : current_st_ed[1]}]})

                                        # 向きの最適化と各経路の重み付けを行う
                                        route_info = optimize_routeinfo(past_ed_node, current_node, route_info[0]["dlist"])
                                        if len(route_info) >= 2:
                                            route_info = select_one_route(route_info) # addが最大の1つの経路のみ取り出す

                                        # 行き来をstayに
                                        len_pastlist = len(pastlist)
                                        if (len_pastlist >= 2):
                                            past_st_node = [pastlist[1]["start_node"]]
                                            past_st_id   = past_st_node[0]["pcwl_id"]

                                            ### TODO:経路部分一致でstayに ###
                                            current_route = []
                                            for route in route_info[0]["route"]:
                                                current_route.append(route["direction"])

                                            q_lt  = data["id"]["get_time_no"]
                                            q_gte = shift_seconds(q_lt, - min_interval)
                                            past_route = []
                                            past_route += db.pfvmacinfo.find({"mac":data["id"]["mac"], "datetime":{"$gte":q_gte,"$lt":q_lt}}).sort("datetime",-1)
                                            if (len(past_route) == 1):
                                            
                                                if (route_partial_match(current_route,past_route[0]["route"])):
                                                    # print("alt_stay")
                                                    # data_lists_"stay" append
                                                    data_lists_stay.append(append_data_lists_stay_alt(data["id"]["mac"], tmp_startdt, tmp_enddt, pastlist[0]["start_node"], data_lists_stay))
                                                    # pastlist update
                                                    update_pastlist_alt(pastd[0], tmp_enddt, num, data["nodelist"], pastlist[0]["start_node"])
                                                    save_pastd(pastd[0], tmp_enddt)
                                                    ins_flag = True
                                                    break

                                        for route in route_info[0]["route"]:
                                            after_node_id = route["direction"][1]
                                            after_node_info = db.pcwlnode.find_one({"floor":tmp_floor,"pcwl_id":after_node_id})
                                            if (len(after_node_info["next_id"])>=3):
                                                intersection_flag = True
                                                break

                                        if intersection_flag:
                                            se_data = append_data_lists(num, data, tmp_startdt, tmp_enddt, pastlist[0]["start_node"], data_lists)
                                            se_data["end_node"] = [{"floor":tmp_floor,"pcwl_id":after_node_id,"rssi":None}]
                                            # print(se_data)
                                            data_lists.append(se_data)
                                            update_pastlist_intersection(pastd[0], tmp_enddt, num, data["nodelist"], after_node_info)
                                            save_pastd(pastd[0], tmp_enddt)
                                            ins_flag = True
                                            # print("intersection stop")
                                            break

                                        # data_lists append
                                        data_lists.append(append_data_lists(num, data, tmp_startdt, tmp_enddt, pastlist[0]["start_node"], data_lists))
                                        # pastlist update
                                        update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"])
                                        save_pastd(pastd[0], tmp_enddt)
                                        # print("flow1")
                                        ins_flag = True
                                        break

                                else:
                                    # pastlist update
                                    update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"])
                                    save_pastd(pastd[0], tmp_enddt)
                                    print("over repeat_cnt")
                                    ins_flag = True
                                    break

                            # stay
                            elif (tmp_node["pcwl_id"] == pastlist[0]["start_node"]["pcwl_id"])and(tmp_floor == pastlist[0]["start_node"]["floor"]):
                                # print("stay")
                                if (pastd[0]["nodecnt_dict"][tmp_floor][tmp_id_str] <= repeat_cnt):
                                    # data_lists_stay append
                                    data_lists_stay.append(append_data_lists_stay(num, data, tmp_startdt, tmp_enddt, tmp_node, data_lists_stay))
                                    # pastlist update
                                    update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"])
                                    save_pastd(pastd[0], tmp_enddt)
                                    # print("stay1")
                                    ins_flag = True
                                    break
                                else:
                                    update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"])
                                    save_pastd(pastd[0], tmp_enddt)
                                    # print("stay2")
                                    ins_flag = True
                                    break
                            # other floor
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

                # pastlist == []
                else:
                    # print("6:not append")
                    for num in range(0, node_cnt):
                        tmp_node   = data["nodelist"][num]
                        if (tmp_node["rssi"] >= TH_RSSI):
                            # nodecnt_dict update
                            # pastlist update
                            update_pastlist(pastd[0], tmp_enddt, num, data["nodelist"])
                            save_pastd(pastd[0], tmp_enddt)
                            break

            count_all += 1
            if (ins_flag):
                update_maclist(data["id"]["mac"])

        data_lists      = reverse_list(data_lists, "start_time")
        data_lists_stay = reverse_list(data_lists_stay, "start_time")

    # pastdata check　/ dataが取れなかった場合一旦stay
    past_maclist = db.pastmaclist.find()
    for data in past_maclist:
        mac = data["_id"]["mac"]
        pastmacdata = db.pastdata.find_one({"mac":mac})
        pastmacdata["pastlist"] = reverse_list(pastmacdata["pastlist"], "dt")

        make_nodecnt_dict(pastmacdata["pastlist"], all_st_time, pastmacdata["nodecnt_dict"])
        if (len(pastmacdata["pastlist"]) != 0):
            for node in pastmacdata["pastlist"]:
                if(all_st_time - node["dt"] <= KEEP_ALIVE):
                    if (node["alive"]):
                        data_lists_stay.append(append_data_lists_stay_alt(mac, shift_seconds(all_st_time, -5), all_st_time, node["start_node"], data_lists_stay))
                        update_pastlist_keep_alive(pastmacdata, all_st_time, 0, [], node["start_node"])
                        # print("keep alive stay")
                        save_pastd(pastmacdata, all_st_time)
                        break

    # save_pfvinfo.py へ渡す
    make_pfvinfo(data_lists,db.pfvinfo,min_interval)
    make_stayinfo(data_lists_stay,db.stayinfo,min_interval)
    make_pfvmacinfo(data_lists,db.pfvmacinfo,min_interval)
    make_staymacinfo(data_lists_stay,db.staymacinfo,min_interval)

# 実験用 mac→name フィルタ
def name_filter(mac):
    if mac == "90:b6:86:52:77:2a":
        name = "Galaxy(S)"
    elif mac == "80:be:05:6c:6b:2b":
        name = "iPhone6Plus(Y)"
    elif mac == "98:e0:d9:35:92:4d":
        name = "iPhone6(A)"
    elif mac == "18:cf:5e:4a:3a:17":
        name = "Dynabook(A)"
    elif mac == "18:00:2d:62:6c:d1":
        name = "XperiaVL(A)"
    else:
        name = mac
    return name

def get_min_distance(floor, node1, node2):
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
    nodecnt_dict = {}
    for floor in FLOOR_LIST:
        nodecnt_dict.update({floor:{}})
        for num in range(MIN_NODE_NUM, MAX_NODE_NUM+1):
            nodecnt_dict[floor].update({str(num):0})

    return nodecnt_dict

def make_nodecnt_dict(node_history, get_time_no, nodecnt_dict):
    remove_list = []
    loop_cnt = 0
    for history in node_history[:]:
        his_node_cnt = min(len(history["node"]),3)
        if not(get_time_no - time_range <= history["dt"] <= get_time_no):
            for h_num in range(0, his_node_cnt):
                tmp_id   = history["node"][h_num]["pcwl_id"]
                tmp_floor = history["node"][h_num]["floor"]
                nodecnt_dict[tmp_floor].update({str(tmp_id) : nodecnt_dict[tmp_floor][str(tmp_id)]-1})
                if nodecnt_dict[tmp_floor][str(tmp_id)] == -1:
                    print("---------! nodecnt_dict -1 error !---------")
                    pass
            node_history.remove(history)

def update_nodecnt_dict(node_cnt, min_interval, data, nodecnt_dict):
    for num in range(0, node_cnt):
        tmp_id   = data["nodelist"][num]["pcwl_id"]
        tmp_floor = data["nodelist"][num]["floor"]
        nodecnt_dict[tmp_floor].update({str(tmp_id) : nodecnt_dict[tmp_floor][str(tmp_id)]+1})
        if nodecnt_dict[tmp_floor][str(tmp_id)] > int_time_range / min_interval + 1:
            print("---------! nodecnt_dict > 7 error !---------")
            pass

def append_data_lists(num, data, tmp_startdt, tmp_enddt, tmp_node_id, data_lists):
    if tmp_enddt < tmp_startdt:
        print("---------! ed > st error !---------")
    if (tmp_enddt - tmp_startdt).seconds > int_time_range:
        print("---------! flow ed-st>60 error !---------")
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
    if tmp_enddt < tmp_startdt:
        print("---------! ed > st error !---------")
    if (tmp_enddt - tmp_startdt).seconds > int_time_range:
        print("---------! stay ed-st>60 error !---------")
    se_data =  {"mac":data["id"]["mac"],
                "start_time":tmp_startdt,
                "end_time"  :tmp_enddt,
                "interval"  :(tmp_enddt - tmp_startdt).seconds,
                "start_node":tmp_node_id["pcwl_id"],
                "end_node"  :data["nodelist"][num]["pcwl_id"],
                "floor"     :tmp_node_id["floor"],
                }
    return se_data

# 行き来した場合stayに
def append_data_lists_stay_alt(mac, tmp_startdt, tmp_enddt, tmp_node_id, data_lists_stay):
    if tmp_enddt < tmp_startdt:
        print("---------! ed > st error !---------")
    if (tmp_enddt - tmp_startdt).seconds > int_time_range:
        print("---------! stay ed-st>60 error !---------")
    se_data =  {"mac":mac,
                "start_time":tmp_startdt,
                "end_time"  :tmp_enddt,
                "interval"  :(tmp_enddt - tmp_startdt).seconds,
                "start_node":tmp_node_id["pcwl_id"],
                "end_node"  :tmp_node_id["pcwl_id"],
                "floor"     :tmp_node_id["floor"],
                }
    # print(se_data)
    return se_data

def update_pastlist(pastd, get_time_no, num, nodelist):
    past_dict = {"dt":get_time_no, "start_node":nodelist[num], "node":nodelist, "alive":True} 
    pastd["pastlist"].append(past_dict)

def update_pastlist_intersection(pastd, get_time_no, num, nodelist, start_node):
    past_dict = {"dt":get_time_no, "start_node":start_node, "node":nodelist, "alive":True} 
    pastd["pastlist"].append(past_dict)

def update_pastlist_alt(pastd, get_time_no, num, nodelist, start_node):
    past_dict = {"dt":get_time_no, "start_node":start_node, "node":nodelist, "alive":True} 
    pastd["pastlist"].append(past_dict)

def update_pastlist_keep_alive(pastd, get_time_no, num, nodelist, start_node):
    past_dict = {"dt":get_time_no, "start_node":start_node, "node":nodelist, "alive":False}
    pastd["pastlist"].append(past_dict)

def save_pastd(pastd,update_dt):
    pastd = {"mac":pastd["mac"],
             "update_dt":update_dt,
             "nodecnt_dict":pastd["nodecnt_dict"],
             "pastlist":pastd["pastlist"],
            }
    db.pastdata.remove({"mac":pastd["mac"]})
    db.pastdata.save(pastd)

def fix_velocity(floor, interval):
    # 各floor速度対応
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
    data_list = sorted(data_list, key=lambda x:x[str(sort_key)], reverse=True)
    return data_list
    
def make_pastmaclist():
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
    if (db.pastmaclist.find({"_id.mac":mac}).count() == 1):
        db.pastmaclist.remove({"_id.mac":mac})
