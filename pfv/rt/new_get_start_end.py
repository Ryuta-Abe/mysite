# -*- coding: utf-8 -*-
import json, math, datetime, locale, sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
from save_pfvinfo import *
from convert_ip import convert_ip
from convert_nodeid import convert_nodeid
from convert_datetime import shift_seconds
from classify import classify
from mongoengine import *
from pymongo import *
from Class import *
from datetime import *
from examine_route import isinside
from new_get_coord import get_distance_between_points, get_dividing_point
import numpy as np

client = MongoClient()
db = client.nm4bd
db.tmpcol.create_index([("_id.get_time_no", ASCENDING), ("_id.mac", ASCENDING)])

# CONST
# MIN_NODE_NUM = 1
# MAX_NODE_NUM = 27
FLOOR_LIST   = ["W2-6F","W2-7F","W2-8F","W2-9F","kaiyo"]
int_time_range = 30
time_range = timedelta(seconds=int_time_range) # 過去の参照時間幅設定
TH_RSSI    = -80
repeat_cnt = 99
INT_KEEP_ALIVE = 15
KEEP_ALIVE = timedelta(seconds=INT_KEEP_ALIVE)
# 分岐点で止める機能
STOP_AT_INTERSECTION = True
# 分岐点で止めたあとに5sec stayさせる機能(上がTrueのときのみ利用可)
STAY_AFTER_INTERSECTION = False
MIN_INTERVAL = 5
MAX_SPEED = 60
STAY_ROUNDING_ERROR = 0.01
MAC_HEAD = "00:11:81:10:01:"

# use Machine-Learning
USE_ML = True

def get_start_end(all_st):
    """
    開始・終了の時刻・地点を決定するモジュール
    @param  all_st : datetime 開始時刻
    """
    global flow_count
    global stay_count
    flow_count = 0
    stay_count = 0

    # 希望のPRデータのみ抽出
    pr_data_list = db.tmpcol.find({"_id.mac":{"$regex":MAC_HEAD}}).sort([("_id.mac",ASCENDING),("_id.get_time_no",ASCENDING)])
    make_pastmaclist()
    tag_count = db.pastmaclist.count()
    if(pr_data_list.count() != 0):
        pr_data_list_tmp = []
        for pr_data in pr_data_list:  # 各タグのある時刻のPRデータに対して処理を行う
            pr_data_list_tmp.append(pr_data)
            # PRデータの加工を行い、RSSIを抽出する
            pr_data,largest_floor, pcwl_id_list, rssi_list = remake_pr_data(pr_data)
            result = get_analyzed_pos(pr_data, largest_floor, rssi_list)
            if result == 0:
                update_maclist(pr_data["id"]["mac"])
            else:
                print("plz step in to investigate")
                # result = get_analyzed_pos(pr_data, largest_floor, rssi_list)
                print("result(get_analyzed_pos): ", result)
                print("pr_data",pr_data)
    
    if (db.pastmaclist.find() != 0): #  当該タグのPRデータが取得できなかった場合（ex:電源断・ネットワークエラー）
        lost_mac_list = []
        for unavailable_mac in db.pastmaclist.find():
            mac = unavailable_mac["_id"]["mac"]
            pastd = db.pastdata.find_one({"mac":mac})
            # pastlist = reverse_list(pastd["pastlist"], "dt")
            pastlist = pastd["pastlist"]
            if (len(pastlist) != 0):
                for past in pastlist:
                    if(all_st - past["dt"] <= KEEP_ALIVE) and (past["alive"]): # 現在のデータが取れていないが、最新取得時刻からKEEP_ALIVE以下しか経過していない場合
                        # data_lists_stay.append(append_data_lists_stay_alt(mac, shift_seconds(all_st_time, -5), all_st_time, past["start_past"], data_lists_stay))
                        # update_pastlist_keep_alive(pastd, all_st_time, 0, [], past["start_node"])
                        # print("keep alive stay")
                        pastlist.append({"dt":all_st, "floor":past["floor"], "position":past["position"],"nodelist":[], "alive":False, "arrive_intersection":False})  # TODO: dt -> datetime
                        save_pastd(pastd)
                        make_staymacinfo(past["floor"],mac,all_st,past["position"])
                        stay_count += 1
                        break
                else: # 現在のデータがとれておらず、最新取得時刻からKEEP_ALIVEも経過しており、どこにいるか分からない場合
                    lost_mac_list.append(mac)

    # make_pfvmacinfo(data_lists,db.pfvmacinfo,min_interval)
    # make_staymacinfo(data_lists_stay,db.staymacinfo,min_interval)

    print("----",all_st,"----",end="")

    if(flow_count + stay_count != tag_count):
        print("flow: ", flow_count, " / ", tag_count)
        print("stay: ", stay_count, " / ", tag_count)        
        print("Error: Data Lost:", lost_mac_list)
    else:
        print("was analyzed successfully!")


def get_analyzed_pos(pr_data, floor, rssi_list):
    global flow_count
    global stay_count
    # RSSI上位3つまでPRデータを参照するため、ノード数node_cnt(3以下)を算出
    node_cnt = min(len(pr_data["nodelist"]), 3)
    nodelist = pr_data["nodelist"]
    dt = pr_data["id"]["get_time_no"]  #  現在時刻
    mac = pr_data["id"]["mac"]

    # nodelistを機械学習を適応し整形({"floor","position","rssi"})に
    if USE_ML:
        nodelist = []
        desc_index, label_list = classify(floor, rssi_list)
        for i in range(3):
            # label = label_list[desc_index[i]]
            label = label_list[i]

            if abs(np.round(label)- label) < 0.001:
                pcwl_id = int(np.round(label))
                node = Node(floor, pcwl_id)
                position = node.position.position
            else:
                label = float(label)
                if label == 9.1:
                    prev_node = 9
                    next_node = 10
                elif label == 18.2:
                    prev_node = 18
                    next_node = 20
                else:
                    prev_node = int(label)
                    next_node = round((label - prev_node)*100)
                    if next_node % 10 == 0:  # next_nodeが10の倍数⇒next_nodeの桁数が1桁
                        next_node = round(next_node / 10)
                position = [prev_node,1,1,next_node]
                position = get_dividing_point(floor,position[0],position[1],position[2],position[3])
            
            predict_dict = {"floor":floor, "position":position, "rssi":-50-i*10}
            nodelist.append(predict_dict)
    else:
        for node in nodelist:
            node_class = Node(node["floor"],node["pcwl_id"])
            del(node["pcwl_id"])
            node["position"] = node_class.position.position
    # 以上によりnodelistは{"floor","position","rssi"}に(positionはposition list)

    pastd = []
    pastd += db.pastdata.find({"mac":pr_data["id"]["mac"]})

    # update_dtを下回る異常データがいるか確認
    if(pastd != []): 
        # pastlist = pastd[0]["pastlist"]
        # pastlist = reverse_list(pastlist,"dt")
        # pastd[0]["pastlist"] = reverse_list(pastd[0]["pastlist"],"dt")
        pastlist = pastd[0]["pastlist"]

        # pastlist = reverse_list(pastd[0]["pastlist"], "dt")
        # pastlist = pastd[0]["pastlist"]
        if(dt <= pastlist[-1]["dt"]):
            print("0:(dt < update_dt)")
            return -1

    # 無ければ初期nodecnt_dict, 初期pastlistを作成
    else:
        for num in range(0, node_cnt):
            node = nodelist[num]
            if (node["rssi"] >= TH_RSSI):
                init_pastd = {"mac":mac, "pastlist":[]}
                pastd.append(init_pastd)
                pastlist = pastd[0]["pastlist"]
                past_data = {"dt":dt, "floor":floor, "position":nodelist[num]["position"],"nodelist":nodelist, "alive":True, "arrive_intersection":False}
                pastlist.append(past_data)
                save_pastd(pastd[0])
                return 0
        else:  # 全てのRSSIが閾値を下回った場合
            return -1
        # past_dict = {"mac":mac, "pastlist":[]}  ## TODO: update_dtの必要性
        # pastd.append(past_dict)

    # pastlist = pastd[0]["pastlist"]
    # pastlist = reverse_list(pastlist, "dt")
    pastlist = pastd[0]["pastlist"]

    # if pastlist == []:  #  過去の位置情報が存在しない場合
    #     for num in range(0, node_cnt):
    #         node = nodelist[num]
    #         if (node["rssi"] >= TH_RSSI):
    #             pastd[0]["pastlist"].append({"dt":dt, "floor":floor, "position":nodelist[num]["position"],"nodelist":nodelist, "alive":True, "arrive_intersection":False})
    #             save_pastd(pastd[0])
    #             return 0
    #     else:  # 全てのRSSIが閾値を下回った場合
    #         return -1

    
    recent = pastlist[-1]  # 直近の(MIN_INTERVAL前の)pastlist
    recent_pos = recent["position"]
    if STAY_AFTER_INTERSECTION and recent["arrive_intersection"]:  # 交差点到着又は交差点滞留フィルタ適応後に交差点STAYがONでかつ、前回到着した場合
        pastlist.append({"dt":dt,"floor":floor, "position":recent_pos,"nodelist":nodelist, "alive":True, "arrive_intersection":False})  # TODO: 名前の変更
        make_staymacinfo(floor,mac,dt,recent_pos)
        stay_count += 1
        save_pastd(pastd[0])
        return 0
    # 過去の所在位置データのpastlistを取得（TODO:廃止）
    # pastlist = pastd[0]["pastlist"]
    for node in nodelist:  # RSSIが大きい順に各種フィルタを適応し、最終位置を決定する
        if (node["rssi"] < TH_RSSI):  # 一件目のnodeでRSSI小⇒いずれも小
            return -1
        position = node["position"]  # 仮の測位位置position_listを決定

        # stayの場合
        if is_same_position(position,recent_pos) and (floor == recent["floor"]):  
            pastlist.append({"dt":dt,"floor":floor, "position":position,"nodelist":nodelist, "alive":True, "arrive_intersection":False})
            save_pastd(pastd[0])
            make_staymacinfo(floor,mac,dt,position)
            stay_count += 1

        ## flowの場合
        elif not is_same_position(position,recent_pos) and (floor == recent["floor"]):
            pfv_route = get_pfvmacinfo(floor,mac,dt,Position(recent_pos,floor),Position(position,floor))  # 仮のpfv_route（flowをノードを境に分解したもので、ex: [[[1,10.5,17,2],[2,0,54,3]],[[2,0,54,3],[2,14,40,3]]]）
            if not recent["alive"]:  # 前回の場所が存在しない場合は、フィルタを適応せずに保存
                pastlist.append({"dt":dt,"floor":floor, "position":position,"nodelist":nodelist, "alive":True, "arrive_intersection":False})
                save_pastd(pastd[0])
                make_pfvmacinfo(floor,mac,dt,pfv_route)
                flow_count += 1
                return 0
            if recent["alive"] and is_move_too_far(floor,Position(recent_pos,floor),Position(position,floor)):  # 移動距離フィルタ
                continue
            if is_back_and_forth(floor,mac,dt,position):  # 逆行防止フィルタ
                pastlist.append({"dt":dt,"floor":floor, "position":recent_pos,"nodelist":nodelist, "alive":True, "arrive_intersection":False})  # TODO: 名前の変更
                save_pastd(pastd[0])
                make_staymacinfo(floor,mac,dt,recent_pos)
                stay_count += 1
                return 0
            new_pfv_route = find_intersection_and_update_route(floor,pfv_route)
            if STOP_AT_INTERSECTION and new_pfv_route is not None:  # 交差点通過時にstayとする
                intersection = new_pfv_route[-1][-1]
                pastlist.append({"dt":dt,"floor":floor, "position":intersection,"nodelist":nodelist, "alive":True, "arrive_intersection":True})  # TODO: pfvmacinfo
                save_pastd(pastd[0])
                make_pfvmacinfo(floor,mac,dt,new_pfv_route)
                flow_count += 1
            else:  # 普通にflow
                pastlist.append({"dt":dt,"floor":floor, "position":position,"nodelist":nodelist, "alive":True, "arrive_intersection":False})
                save_pastd(pastd[0])
                make_pfvmacinfo(floor,mac,dt,pfv_route)
                flow_count += 1
            return 0

        # 新しいフロアの場合
        else:
            pastlist.append({"dt":dt,"floor":floor, "position":position,"nodelist":nodelist, "alive":True, "arrive_intersection":False})
            save_pastd(pastd[0])
        return 0

def remake_pr_data(pr_data):
    """
    PRデータの加工とRSSIの組の抽出を行い、機械学習の前処理に相当
    @return pcwl_id_list: [1,2,3,5,7]のようなpcwl_idを昇順に並べたリスト
    @return rssi_list: pcwl_id_listに対応するRSSIの組
    """
    # node_listをdbmの降順に(大きなものから)並べなおす
    pr_data["nodelist"] = reverse_list(pr_data["nodelist"],"dbm")
    nodelist = pr_data["nodelist"]

    # RSSI最大のノードがあるfloorの必要データ作成
    for node in nodelist:
        node = Node(node["ip"])
        largest_floor = node.floor
        if largest_floor != "Unknown":
            break

    pcwl_id_list = []  # pcwl_idはとびとびの値であるから、[1,2,3,5,7]のようなpcwl_idを昇順に並べたリスト
    floor_node_col = db.pcwlnode.find({"floor":largest_floor}).sort("pcwl_id",ASCENDING)
    for node in floor_node_col:
        pcwl_id_list.append(node["pcwl_id"])
    rssi_list = [-99] * len(pcwl_id_list)
    
    # nodelistデータ({"floor","pcwl_id","rssi"}) reform, tmpcol_backupに保存
    for list_data in pr_data["nodelist"][:]:
        node = Node(list_data["ip"])
        list_data["floor"]   = node.floor
        list_data["pcwl_id"] = node.pcwl_id
        list_data["rssi"] = list_data["dbm"]
        del(list_data["ip"])
        del(list_data["dbm"])
        # floor error
        if list_data["floor"] == "Unknown":
            data["nodelist"].remove(list_data)

        # RSSIが最大のfloorのデータか否かで分岐
        if list_data["floor"] == largest_floor:
            if list_data["pcwl_id"] in pcwl_id_list:
                index = pcwl_id_list.index(list_data["pcwl_id"])
                rssi_list[index] = list_data["rssi"]

    pr_data["id"] = pr_data["_id"]
    del(pr_data["_id"])
    db.tmpcol_backup.insert(pr_data)

    return pr_data, largest_floor, pcwl_id_list, rssi_list

        

def is_same_position(position_list1,position_list2):
    """
    2つのposition_listが同一かどうか（移動していないかどうか）判定
    @param position_list1: 1つめのposition_list([prev_node,prev_dist,next_dist,next_node])
    @param position_list2: 2つめのposition_list([prev_node,prev_dist,next_dist,next_node])
    @return is_same_position: Bool 2つのposition_listが同一かどうか
    """
    prev_node1,prev_distance1,next_distance1,next_node1 = position_list1
    prev_node2,prev_distance2,next_distance2,next_node2 = position_list2

    if (prev_node1 == next_node2) and (next_node1 == prev_node2):
        position_list2 = Position(position_list2,floor).reverse_order()
    if (prev_node1 == prev_node2) and (next_node1 == next_node2):
        if (abs(prev_distance1 - prev_distance2) <= STAY_ROUNDING_ERROR) and (abs(next_distance1 - next_distance2) <= STAY_ROUNDING_ERROR):
            return True
    return False
            
# def save_pastd(pastd):
#     """
#     pastd(過去データ)更新用
#     各macに対する最終更新時刻update_dtを更新する
#     @param  pastd:dict
#     @param  update_dt:datetime
#     """
#     pastd = {"mac":pastd["mac"],
#              "pastlist":pastd["pastlist"]}
#     db.pastdata.remove({"mac":pastd["mac"]})
#     db.pastdata.save(pastd)

def is_move_too_far(floor,recent_pos,position):
    """
    移動距離フィルタ

    """
    distance,_ = get_distance_between_points(floor,position,recent_pos,True)
    if (distance > MAX_SPEED * MIN_INTERVAL):
        return True
    else:
        return False

def is_back_and_forth(floor,mac,dt,position):
    """

    @param dt: positionに到着した現在時刻
    @param position: 逆行したかどうか判定されるposition


    """
    ## TODO: rounding
    def isinside_ne(start_position,target_position,end_position): # isinsideのposition_list版で、条件が>=でなく>にした版
        start_posx, start_posy = start_position.get_pos_xy()
        end_posx, end_posy = end_position.get_pos_xy()
        target_posx, target_posy = target_position.get_pos_xy()
        if (start_posx <= target_posx < end_posx) and (start_posy <= target_posy < end_posy):
            return True
        if (start_posx >= target_posx > end_posx) and (start_posy >= target_posy > end_posy):
            return True
        else:
            return False

    past_st_dt = shift_seconds(dt,- 2 * MIN_INTERVAL)
    past_ed_dt = shift_seconds(dt, - MIN_INTERVAL)
    past_pfvmacinfo = db.pfvmacinfo.find_one({"mac":mac, "datetime":{"$gte":past_st_dt,"$lt":past_ed_dt}})
    if past_pfvmacinfo is None:
        return None

    past_pfv_route = past_pfvmacinfo["route"]
    for past_route in past_pfv_route:
        if isinside_ne(Position(past_route[0],floor),Position(position,floor),Position(past_route[1],floor)):  #通常のisinsideではなく、isinside_neを用いる
            return True
    else:
        return False

def find_intersection_and_update_route(floor,pfv_route):
    """
    ルート上に交差点が存在するか判定し、あれば、更新したPfv_routeを返す
    @param pfv_route: [[position_list position_list],..,]
    @return intersection or None: 存在すれば交差点のPosition
    """
    new_pfv_route = []
    for route in pfv_route:
        new_pfv_route.append(route)
        one_end_position = route[1]
        if Position(one_end_position,floor).is_intersection():
            return new_pfv_route
    else:
        return None


def get_via_positions_and_intersection(floor,dlist,return_position_list_flag = False):
    via_positions = []
    intersection = None
    for direction in dlist:
        two_positions = []
        for pcwl_id in direction["direction"]:
            node = Node(floor,pcwl_id)
            position = node.position # Position Class
            if node.is_intersection():
                intersection = position
            if return_position_list_flag: # position_listで返す
                two_positions.append(position.position)
            else:
                two_positions.append(position)
        via_positions.append(two_positions)
    return via_positions, intersection

def get_pfvmacinfo(floor, mac, datetime, start_position,end_position):
    """
    @param start_position: Position Class 開始Position

    """
    _,route_index = get_distance_between_points(floor,start_position,end_position,True)
    pfv_route = []
    # past_start_pos = P(A1,?,?,B1), past_end_pos = Q(A2,?,?,B2)とする。

    #-4: B1 = B2の時　　　　　　 A1-P-B1====B2-Q-A2
    if(route_index == -4):
        via_position = Node(floor,start_position.next_node).position.position

    #-3: A1 = B2の時　　　　　　 B1-P-A1====B2-Q-A2
    if(route_index == -3):
        via_position = Node(floor,start_position.prev_node).position.position

    #-2: B1 = A2の時　　　　　　 A1-P-B1====A2-Q-B2
    if(route_index == -2):
        via_position = Node(floor,start_position.next_node).position.position
    #-1: A1 = A2の時　　　　　　 B1-P-A1====A2-Q-B2
    if(route_index == -1):
        via_position = Node(floor,start_position.prev_node).position.position

    if(route_index < 0): # 上記4パターンに共通の処理
        if not is_same_position(start_position.position,via_position):
            pfv_route.append([start_position.position,via_position])
        if not is_same_position(via_position,end_position.position):
            pfv_route.append([via_position, end_position.position])
    
    # 0: 同一線分上に存在(A1=A2とA1=B2のパターン有り)
    if(route_index == 0):
        if(start_position.prev_node == end_position.next_node):
            end_position.reverse_order()
        if(start_position.prev_node == end_position.prev_node):
            pfv_route.append([start_position.position,end_position.position])

    # 1:同一経路上に⇒のように並ぶ B1-P-A1----A2-Q-B2       
    if(route_index == 1):
        ideal_dlist = db.idealroute.find_one({"$and":[{"floor" : floor},{"query" : start_position.prev_node}, {"query" : end_position.prev_node}]})["dlist"]

    # 2:同一経路上に⇒のように並ぶ A1-P-B1----A2-Q-B2
    if(route_index == 2):
        ideal_dlist = db.idealroute.find_one({"$and":[{"floor" : floor},{"query" : start_position.next_node}, {"query" : end_position.prev_node}]})["dlist"]
        # via_positions, intersection = get_via_positions_and_intersection(floor,ideal_route_info,True)

    # 3:同一経路上に⇒のように並ぶ B1-P-A1----B2-Q-A2
    if(route_index == 3):
        ideal_dlist = db.idealroute.find_one({"$and":[{"floor" : floor},{"query" : start_position.prev_node}, {"query" : end_position.next_node}]})["dlist"]
        # via_positions, intersection = get_via_positions_and_intersection(floor,ideal_route_info,True)

    # 4:同一経路上に⇒のように並ぶ B1-P-A1----A2-Q-B2
    if(route_index == 4):
        ideal_dlist = db.idealroute.find_one({"$and":[{"floor" : floor},{"query" : start_position.next_node}, {"query" : end_position.next_node}]})["dlist"]
        # via_positions, intersection = get_via_positions_and_intersection(floor,ideal_route_info,True)

    if(route_index > 0):
        if(end_position.prev_node < start_position.prev_node):
            dlist = get_reverse_dlist(ideal_dlist)
        via_positions, _ = get_via_positions_and_intersection(floor,ideal_dlist,True)
        pfv_route = via_positions
        if start_position.prev_dist != 0:
            first_route = [start_position.position,via_positions[0][0]]
            pfv_route.insert(0,first_route)
        if end_position.prev_dist != 0:
            last_route = [via_positions[-1][-1],end_position.position]
            pfv_route.append(last_route)
    
    return pfv_route
    
def make_pfvmacinfo(floor, mac, datetime, pfv_route):
    db.pfvmacinfo.insert({"datetime":datetime,"mac":mac,"route":pfv_route,"floor":floor})

def make_staymacinfo(floor, mac, datetime, stay_position):
    db.staymacinfo.insert({"datetime":datetime,"mac":mac,"position":stay_position,"floor":floor})

def get_reverse_dlist(dlist):
    dlist.reverse()
    for direction in dlist:
        direction["direction"].reverse()
    return dlist

# def isinside_route(start_position,target_position,end_position,via_positions):
#     """
#     target_positionがstart_positionとend_positionの内側にあるか判定する関数で、isinside()の改良版
#     @start_position: Position Class 始発点
#     @end_position: Position Class 終着点
#     @target_position: 間にあるか求めたい点
#     @return: Bool 間にあるかどうか
#     """

#     if isinside(via_positions[-1][-1], target_position, end_position, True ,floor):  # end_positionとその近傍のvia_position間において内側にあるかどうか判定
#         return True
#     if isinside(start_position,target_position,via_positions[0][0], True ,floor):
#         return True
#     for i in range(len(via_positions)):
#         if isinside(via_positions[i][0], target_position, via_positions[i][1], True, floor):
#             return True
#     else:
#         return False

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

def save_pastd(pastdata):
    """
    pastd(過去データ)更新用
    各macに対する最終更新時刻update_dtを更新する
    @param  pastd:dict
    @param  update_dt:datetime
    """
    db.pastdata.remove({"mac":pastdata["mac"]})
    
    pastlist = pastdata["pastlist"]
    update_dt = pastlist[-1]["dt"]
    # pastdata["pastlist"] = [past for past in pastlist if ((update_dt - past["dt"]).seconds >= (INT_KEEP_ALIVE * 2))]
    for i,past in enumerate(pastlist[:]):
        if((update_dt - past["dt"]).seconds >= (INT_KEEP_ALIVE * 2)):
            pastlist.remove(past)
    
    db.pastdata.save(pastdata)


# def init_nodecnt_dict():
#     """
#     nodecnt_dictの初期化
#     @return nodecnt_dict:dict
#         (ex: {"W2-7F":{1:0,2:0,...},...})
#     """
#     nodecnt_dict = {}
#     for floor in FLOOR_LIST:
#         nodecnt_dict.update({floor:{}})
#         for num in range(MIN_NODE_NUM, MAX_NODE_NUM+1):
#             nodecnt_dict[floor].update({str(num):0})
#     return nodecnt_dict