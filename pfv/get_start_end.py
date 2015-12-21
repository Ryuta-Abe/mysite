# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test, tmpcol, pcwlroute
from pfv.save_pfvinfo import make_pfvinfo, make_pfvmacinfo, make_stayinfo, make_staymacinfo
from pfv.make_pcwltime import make_pcwltime
from pfv.convert_nodeid import *
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale
from datetime import datetime, timedelta

client = MongoClient()
db = client.nm4bd
db.tmpcol.create_index([("get_time_no", DESCENDING), ("mac", ASCENDING)])

# CONST
MIN_NODE_NUM = 1
MAX_NODE_NUM = 27
FLOOR_LIST   = ["W2-6F","W2-7F"]
time_range = timedelta(minutes=1) # 過去の参照時間幅設定

def get_start_end(request):
  from datetime import datetime, timedelta
  # urlからクエリの取り出し
  algorithm = int(request.GET.get('algorithm', 1))
  
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
  # datas = db.tmpcol.find().sort("_id.get_time_no",-1).sort("_id.mac")
  datas = db.tmpcol.find({"_id.mac":{"$regex":"00:11:81:10:01:"}}).sort("_id.get_time_no",-1).sort("_id.mac")
  # datas = db.tmpcol.find({"_id.mac":"80:be:05:6c:6b:2b"}).sort("_id.get_time_no",-1).sort("_id.mac")
  # datas = db.tmpcol.find({"_id.get_time_no":{"$gte":20150925173500,"$lte":20150925182000}}).limit(5000).sort("_id.get_time_no",-1).sort("_id.mac")

  ### アルゴリズム1 ###
  if algorithm == 1:
    # 1番目の設定
    datas[0]['nodelist'] = sorted(datas[0]['nodelist'], key=lambda x:x["dbm"], reverse=True)
    for tmp_node_id in datas[0]['nodelist']:
      end_node_list.append({"pcwl_id":convert_nodeid(tmp_node_id['node_id'])["node_id"],
                            "floor":convert_nodeid(tmp_node_id['node_id'])["floor"],
                            "rssi":tmp_node_id['dbm'],
                          })
    tmp_node_id = end_node_list[0]

    for data in datas:
      data['id'] = data['_id']
      del(data['_id'])
      data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
      
      for list_data in data['nodelist']:
        list_data['floor']   = convert_nodeid(list_data['node_id'])['floor']
        list_data['pcwl_id'] = convert_nodeid(list_data['node_id'])['node_id']
        del(list_data["node_id"])

      # RSSI上位3つまで参照
      node_cnt = min(len(data["nodelist"]), 3)
      
      # mac確認
      if (data["id"]["mac"] == tmp_mac):
        data['nodelist'] = sorted(data['nodelist'], key=lambda x:x["dbm"], reverse=True)

        end_node_list = []
        for list_data in data['nodelist']:
          tmp_dict = {"pcwl_id":list_data['pcwl_id'],"floor":list_data['floor'],"rssi":list_data['dbm']}
          end_node_list.append(tmp_dict)
        node_history.append({"node":end_node_list, "dt":data['id']['get_time_no']})

        # nodecnt_dict作成
        make_nodecnt_dict(node_history, data, nodecnt_dict)
        update_nodecnt_dict(node_cnt, data, nodecnt_dict)

        # 時間間隔チェック
        if ((data['id']['get_time_no'] - tmp_startdt).seconds <= 60):
          tmp_enddt = data['id']['get_time_no']

          for num in range(0, node_cnt):
            tmp_num   = data["nodelist"][num]['pcwl_id']
            tmp_floor = data["nodelist"][num]['floor']

            # RSSIが一定値より大きい場合
            if (data["nodelist"][num]["dbm"] >= -80):
              # node_idが一致しない場合(flow)
              if (data["nodelist"][num]["pcwl_id"] != tmp_node_id["pcwl_id"])and(data["nodelist"][num]["floor"] == tmp_node_id["floor"]):
                # 出現回数による除外
                if (nodecnt_dict[tmp_floor][tmp_num] <= 4):
                  interval = (tmp_enddt - tmp_startdt).seconds

                  # 経路情報の取り出し
                  d_total = get_min_distance(tmp_node_id["floor"], tmp_node_id["pcwl_id"], data["nodelist"][num]["pcwl_id"])
                  # 妥当な移動距離かチェック
                  if d_total < interval*22:
                    append_data_lists(num, data, tmp_startdt, tmp_enddt, tmp_node_id, data_lists)
                    tmp_node_id = data["nodelist"][num]
                    tmp_startdt = data['id']['get_time_no']
                    count += 1
                    break

                # 出現回数が多いとき
                else:
                  tmp_startdt = data['id']['get_time_no']
                  tmp_node_id = data["nodelist"][num]
                  break

              # node_idが一致(stay)
              elif (data["nodelist"][num]["pcwl_id"] == tmp_node_id["pcwl_id"])and(data["nodelist"][num]["floor"] == tmp_node_id["floor"]):
                append_data_lists_stay(num, data, tmp_startdt, tmp_enddt, tmp_node_id, data_lists_stay)
                tmp_startdt = data['id']['get_time_no']
                tmp_node_id = data["nodelist"][num]
                break

              # floorが異なる場合
              else:
                tmp_startdt = data['id']['get_time_no']
                tmp_node_id = data["nodelist"][num]
                break

            # RSSIが一定値より小さい場合
            else:
              break

        # 時間間隔60秒より大
        else:
          tmp_node_id = end_node_list[0]
          tmp_startdt = data['id']['get_time_no']
          nodecnt_dict = init_nodecnt_dict()
          update_nodecnt_dict(node_cnt, data, nodecnt_dict)

          node_history = []
          node_history.append({"node":end_node_list, "dt":data['id']['get_time_no']})

      # mac異なる場合
      else:
        tmp_mac = data["id"]["mac"]
        tmp_node_id = {"pcwl_id":data["nodelist"][0]["pcwl_id"],"floor":data["nodelist"][0]["floor"],"rssi":data["nodelist"][0]['dbm']} 
        end_node_list = []
        tmp_startdt = data['id']['get_time_no']

        for end_node in data["nodelist"]:
          end_node_list.append(end_node)

        node_history = []
        node_history.append({"node":end_node_list, "dt":data['id']['get_time_no']})
        nodecnt_dict = init_nodecnt_dict()
        update_nodecnt_dict(node_cnt, data, nodecnt_dict)

      count_all += 1

    data_lists = sorted(data_lists, key=lambda x:x["start_time"], reverse=True)
    data_lists_stay = sorted(data_lists_stay, key=lambda x:x["start_time"], reverse=True)

    # import time
    # start = time.time()
    make_pfvinfo(data_lists,db.pfvinfo)
    make_stayinfo(data_lists_stay,db.stayinfo)
    make_pfvmacinfo(data_lists,db.pfvmacinfo)
    make_staymacinfo(data_lists_stay,db.staymacinfo)
    # end = time.time()
    # print("time:"+str(end-start))

    return render_to_response('pfv/get_start_end.html',  # 使用するテンプレート
                               {"datas":data_lists[:2000], "count":count, "count_all":count_all} 
                             ) 

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
  route_info += db.pcwlroute.find({"$and":[ {"floor" : floor}, {"query" : node1}, {"query" : node2} ]})
  # 最小距離算出
  for info in route_info:
    # for part in route:
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
      nodecnt_dict[floor].update({num:0})

  return nodecnt_dict

def make_nodecnt_dict(node_history, data, nodecnt_dict):
  for history in node_history:
    his_node_cnt = min(len(history["node"]),3)
    if (data['id']['get_time_no'] - time_range > history["dt"]):
      for h_num in range(0, his_node_cnt):
        tmp_num   = history["node"][h_num]["pcwl_id"]
        tmp_floor = history["node"][h_num]["floor"]
        nodecnt_dict[tmp_floor].update({tmp_num : nodecnt_dict[tmp_floor][tmp_num]-1})
      node_history.remove(history)

def update_nodecnt_dict(node_cnt, data, nodecnt_dict):
  for num in range(0, node_cnt):
    tmp_num   = data["nodelist"][num]['pcwl_id']
    tmp_floor = data["nodelist"][num]['floor']
    nodecnt_dict[tmp_floor].update({tmp_num : nodecnt_dict[tmp_floor][tmp_num]+1})

def append_data_lists(num, data, tmp_startdt, tmp_enddt, tmp_node_id, data_lists):
  se_data =  {"mac":data["id"]["mac"],
              "start_time":tmp_startdt,
              "end_time"  :tmp_enddt,
              "interval"  :(tmp_enddt - tmp_startdt).seconds,
              "start_node":[tmp_node_id],
              "end_node"  :[data["nodelist"][num]],
              "floor"     :tmp_node_id["floor"],
              }
  data_lists.append(se_data)

def append_data_lists_stay(num, data, tmp_startdt, tmp_enddt, tmp_node_id, data_lists_stay):
  se_data =  {"mac":data["id"]["mac"],
              "start_time":tmp_startdt,
              "end_time"  :tmp_enddt,
              "interval"  :(tmp_enddt - tmp_startdt).seconds,
              "start_node":tmp_node_id["pcwl_id"],
              "end_node"  :data["nodelist"][num]["pcwl_id"],
              "floor"     :tmp_node_id["floor"],
              }
  data_lists_stay.append(se_data)

# not using
# def distance_filter(st_list,ed_list,interval):
#   route_info = [] # 経路情報の取り出し
#   if ed_list == []:
#     return [[],[]]

#   route_info += db.pcwlroute.find({"$and":[
#                                             {"query" : st_list[0]["pcwl_id"]}, 
#                                             {"query" : ed_list[0]["pcwl_id"]}
#                                           ]})
#   route_info = route_info[0]["dlist"]
#   d_total = 0
#   d_total_max = 0
#   for route in route_info:
#     for node in route:
#       d_total += node["distance"]
#     if (d_total > d_total_max):
#       d_total_max = d_total
#   if d_total_max < interval*20:
#     return [st_list,ed_list]
#   else :
#     if (len(st_list)>=2) and (len(ed_list)>=2):
#       if (st_list[1]["rssi"]) > (ed_list[1]["rssi"]):
#         return distance_filter(st_list,ed_list[1:],interval)
#       else :
#         return distance_filter(st_list[1:],ed_list,interval)
#     elif (len(st_list)>=2) and (len(ed_list)==1):
#       return distance_filter(st_list[1:],ed_list,interval)
#     elif (len(st_list)==1) and (len(ed_list)>=2):
#       return distance_filter(st_list,ed_list[1:],interval)
#     else :
#       return [[],[]]
