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

client = MongoClient()
db = client.nm4bd
db.tmpcol.create_index([("get_time_no", DESCENDING), ("mac", ASCENDING)])

def get_start_end(request):
  from datetime import datetime, timedelta

  # urlからクエリの取り出し
  algorithm = int(request.GET.get('algorithm', 1))
  # CONST
  MIN_NODE_NUM = 1
  MAX_NODE_NUM = 27
  FLOOR_LIST   = ["W2-6F","W2-7F"]
  mac_list_experiment = ["90:b6:86:52:77:2a","80:be:05:6c:6b:2b","98:e0:d9:35:92:4d","18:cf:5e:4a:3a:17","18:00:2d:62:6c:d1"]
  
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
  tmp_node_id_list = []

  nodecnt_dict = {}
  for floor in FLOOR_LIST:
    nodecnt_dict.update({floor:{}})
    for num in range(MIN_NODE_NUM, MAX_NODE_NUM+1):
      nodecnt_dict[floor].update({num:0})

  # data取り出し
  datas = db.tmpcol.find().sort("_id.get_time_no",-1).sort("_id.mac")
  # datas = db.tmpcol.find({"_id.mac":"80:be:05:6c:6b:2b"}).sort("_id.get_time_no",-1).sort("_id.mac")
  # datas = db.tmpcol.find({"_id.get_time_no":{"$gte":20150925173500,"$lte":20150925182000}}).limit(5000).sort("_id.get_time_no",-1).sort("_id.mac")

  ### アルゴリズム1 ###
  if algorithm == 1:
    # 1番目の設定
    datas[0]['nodelist'] = sorted(datas[0]['nodelist'], key=lambda x:x["dbm"], reverse=True)
    for tmp_node_id in datas[0]['nodelist']:
      tmp_node_id_list.append({"pcwl_id":convert_nodeid(tmp_node_id['node_id'])["node_id"],
                               "floor":convert_nodeid(tmp_node_id['node_id'])["floor"],
                               "rssi":tmp_node_id['dbm'],
                               })
    tmp_node_id = tmp_node_id_list[0]

    for data in datas:
      data['id'] = data['_id']
      for list_data in data['nodelist']:
        list_data['floor']   = convert_nodeid(list_data['node_id'])['floor']
        list_data['node_id'] = convert_nodeid(list_data['node_id'])['node_id']
        list_data["pcwl_id"] = list_data['node_id']
        del(list_data["node_id"])

      # RSSI上位3つまで参照
      node_cnt = min(len(data["nodelist"]), 3)
      time_range = timedelta(minutes=1)
      
      # mac確認
      if (data["id"]["mac"] == tmp_mac):
        data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
        data['nodelist'] = sorted(data['nodelist'], key=lambda x:x["dbm"], reverse=True)
        end_node_list = []
        tmp_nodelist = []
        for list_data in data['nodelist']:
          tmp_dict = {"pcwl_id":list_data['pcwl_id'],"floor":list_data['floor'],"rssi":list_data['dbm']}
          end_node_list.append(tmp_dict)
          tmp_nodelist.append(tmp_dict)

        node_history.append({"node":tmp_nodelist, "dt":data['id']['get_time_no']})

        # node_history作成
        for history in node_history:
          his_node_cnt = len(history["node"])
          if not(data['id']['get_time_no'] - time_range <= history["dt"]):
            for h_num in range(0, his_node_cnt):
              tmp_num   = history["node"][h_num]["pcwl_id"]
              tmp_floor = history["node"][h_num]["floor"]
              nodecnt_dict[tmp_floor].update({tmp_num : nodecnt_dict[tmp_floor][tmp_num]-1})
            node_history.remove(history)

        for num in range(0, node_cnt):
          tmp_num   = data["nodelist"][num]['pcwl_id']
          tmp_floor = data["nodelist"][num]['floor']
          nodecnt_dict[tmp_floor].update({tmp_num : nodecnt_dict[tmp_floor][tmp_num]+1})

        # 時間間隔チェック
        if ((data['id']['get_time_no'] - tmp_startdt).seconds <= 60):
          tmp_enddt = data['id']['get_time_no']
          del(data['_id'])

          for num in range(0, node_cnt):
            tmp_num   = data["nodelist"][num]['pcwl_id']
            tmp_floor = data["nodelist"][num]['floor']

            # node_idが一致しない場合(flow)
            if (data["nodelist"][num]["pcwl_id"] != tmp_node_id["pcwl_id"])and(data["nodelist"][num]["floor"] == tmp_node_id["floor"]):
              # 出現回数による除外
              if (nodecnt_dict[tmp_floor][tmp_num] <= 4):
                # 経路情報の取り出し
                route_info = [] 
                route_info += db.pcwlroute.find({"$and":[
                                                          {"floor" : tmp_node_id["floor"]},
                                                          {"query" : tmp_node_id["pcwl_id"]}, 
                                                          {"query" : data["nodelist"][num]["pcwl_id"]}
                                                        ]})
                d_total = 0
                interval = (tmp_enddt - tmp_startdt).seconds
                
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

                # 妥当な移動距離かチェック
                if d_total < interval*20:
                  se_data =  {"mac":data["id"]["mac"],
                              "start_time":tmp_startdt,
                              "end_time"  :tmp_enddt,
                              "interval"  :(tmp_enddt - tmp_startdt).seconds,
                              "start_node":[tmp_node_id],
                              "end_node"  :[data["nodelist"][num]],
                              "floor"     :tmp_node_id["floor"],
                              }
                  data_lists.append(se_data)
                  tmp_node_id = data["nodelist"][num]
                  count += 1

                  # # 実験用
                  # if se_data["mac"] in mac_list_experiment:
                  #   se_data["mac"] = name_filter(se_data["mac"])
                  #   data_lists_experiment.append(se_data)
                  break

              # 出現回数が多いとき
              else:
                break

            # node_idが一致(stay)
            elif (data["nodelist"][num]["pcwl_id"] == tmp_node_id["pcwl_id"])and(data["nodelist"][num]["floor"] == tmp_node_id["floor"]):
              se_data =  {"mac":data["id"]["mac"],
                          "start_time":tmp_startdt,
                          "end_time"  :tmp_enddt,
                          "interval"  :(tmp_enddt - tmp_startdt).seconds,
                          "start_node":tmp_node_id["pcwl_id"],
                          "end_node"  :data["nodelist"][num]["pcwl_id"],
                          "floor"     :tmp_node_id["floor"],
                          }
              data_lists_stay.append(se_data)
              break

          tmp_startdt = data['id']['get_time_no']

        # 時間間隔60秒より大
        else:
          tmp_node_id_list = end_node_list
          tmp_node_id = tmp_node_id_list[0]
          tmp_startdt = data['id']['get_time_no']

      # mac異なる場合
      else:
        tmp_mac = data["id"]["mac"]
        tmp_node_id = {"pcwl_id":data["nodelist"][0]["pcwl_id"],"floor":data["nodelist"][0]["floor"],"rssi":data["nodelist"][0]['dbm']} 
        end_node_list = []
        for end_node in data["nodelist"]:
          end_node_list.append(end_node)

        data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
        tmp_startdt = data['id']['get_time_no']
        node_history = []
        tmp_nodelist = []
        for nodedata in data["nodelist"]:
          tmp_nodelist.append(nodedata)

        node_history.append({"node":tmp_nodelist, "dt":data['id']['get_time_no']})
        nodecnt_dict = {}
        for floor in FLOOR_LIST:
          nodecnt_dict.update({floor:{}})
          for num in range(MIN_NODE_NUM, MAX_NODE_NUM+1):
            nodecnt_dict[floor].update({num:0})

        for num in range(0, node_cnt):
          tmp_num   = data["nodelist"][num]['pcwl_id']
          tmp_floor = data["nodelist"][num]['floor']
          nodecnt_dict[tmp_floor].update({tmp_num : nodecnt_dict[tmp_floor][tmp_num]+1})

      count_all += 1

    data_lists = sorted(data_lists, key=lambda x:x["start_time"], reverse=True)
    data_lists_stay = sorted(data_lists_stay, key=lambda x:x["start_time"], reverse=True)
    data_lists_experiment = sorted(data_lists_experiment, key=lambda x:x["start_time"], reverse=True) # 実験用  

    # import time
    # start = time.time()
    make_pfvinfo(data_lists,db.pfvinfo)
    make_stayinfo(data_lists_stay,db.stayinfo)
    # end = time.time()
    # print("time:"+str(end-start))
    # make_pfvinfo(data_lists_experiment,db.pfvinfoexperiment)
    make_pfvmacinfo(data_lists,db.pfvmacinfo)
    make_staymacinfo(data_lists_stay,db.staymacinfo)

    return render_to_response('pfv/get_start_end.html',  # 使用するテンプレート
                               {"datas":data_lists[:2000], "count":count, "count_all":count_all} 
                             ) 


  ##########################################################
  ### アルゴリズム2 ############################################
  ##########################################################
  elif algorithm == 2:
    import time
    start = time.time()

    for data in datas:
      data['id'] = data['_id']

      # macaddrが一致するものを処理
      if (data["id"]["mac"] == tmp_mac):
        data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
        data['nodelist'] = sorted(data['nodelist'], key=lambda x:x["dbm"], reverse=True)

        # intervalによる除外
        if ((data['id']['get_time_no'] - tmp_startdt).seconds <= 60):
          tmp_enddt = data['id']['get_time_no']
          del(data['_id'])

          # 行き来する端末除外
          repeat_cnt = 0
          tmp_nodelist = []
          for nodedata in data["nodelist"]:
            append_nodedata = {"pcwl_id":convert_nodeid(nodedata['node_id']),"rssi":nodedata['dbm']}
            tmp_nodelist.append(append_nodedata)

          node_history.append({"node":tmp_nodelist, "dt":data['id']['get_time_no']})
          for num in range(0, min(len(data["nodelist"]), 3)):
            tmp_num = convert_nodeid(data["nodelist"][num]['node_id'])
            nodecnt_dict.update({tmp_num : nodecnt_dict[tmp_num]+1})

          # PFVのデータリスト生成
          node_cnt = min(len(data["nodelist"]), 3)
          time_range = timedelta(minutes=1)

          for history in node_history:
            if not(data['id']['get_time_no'] - time_range <= history["dt"] <= data['id']['get_time_no'] + time_range):
              for num in range(0, min(len(history["node"]), 3)):
                tmp_num = history["node"][num]["pcwl_id"]
                nodecnt_dict.update({tmp_num : nodecnt_dict[tmp_num]-1})
              node_history.remove(history)
          
          interval = (tmp_enddt - tmp_startdt).seconds
          [st_list,ed_list] = distance_filter(start_nodelist, tmp_nodelist, interval)
          if (nodecnt_dict[convert_nodeid(data["nodelist"][0]["node_id"])] <= 4):
            if (st_list != []) and (ed_list != []):
              se_data =  {"mac":data["id"]["mac"],
                          "start_time":tmp_startdt,
                          "end_time"  :tmp_enddt,
                          "interval"  :(tmp_enddt - tmp_startdt).seconds,
                          "start_node":st_list,
                          "end_node"  :ed_list,
                          }
              if se_data["mac"] in mac_list_experiment:
                se_data["mac"] = name_filter(se_data["mac"])
                data_lists_experiment.append(se_data)
              data_lists.append(se_data)

              count += 1

          # if data["nodelist"][num]["node_id"] != tmp_node_id:
          #   route_info = [] # 経路情報の取り出し
          #   route_info += db.pcwlroute.find({"$and":[
          #                                             {"query" : tmp_node_id}, 
          #                                             {"query" : data["nodelist"][num]["node_id"]}
          #                                           ]})
          #   d_total = 0
          #   interval = (tmp_enddt - tmp_startdt).seconds
            
          #   # 総距離算出
          #   for info in route_info:
          #     # for part in route:
          #     for route in info["dlist"]:
          #       tmp_d_total = 0
          #       for part in route:
          #         tmp_d_total += part["distance"]
          #       if d_total == 0:
          #         d_total = tmp_d_total
          #       if (tmp_d_total < d_total):
          #         d_total = tmp_d_total

          #   if d_total < interval*20:
              # se_data =  {"mac":data["id"]["mac"],
              #             "start_time":tmp_startdt,
              #             "end_time"  :tmp_enddt,
              #             "interval"  :(tmp_enddt - tmp_startdt).seconds,
              #             "start_node":[tmp_node_id],
              #             "end_node"  :[data["nodelist"][num]["node_id"]],
              #             # "start_node":tmp_node_id_list,
              #             # "end_node"  :end_node_list,
              #             }

          #     tmp_node_id = data["nodelist"][num]["node_id"]
              # if repeat_cnt <= 60:
              #   data_lists.append(se_data)
          #       count += 1

          #     # 実験用
          #     if se_data["mac"] in mac_list_experiment:
          #       se_data["mac"] = name_filter(se_data["mac"])
          #       data_lists_experiment.append(se_data)
          #     break

          # # stayデータリスト生成
          # elif data["nodelist"][0]["node_id"] == tmp_node_id:
          #   se_data =  {"mac":data["id"]["mac"],
          #               "start_time":tmp_startdt,
          #               "end_time"  :tmp_enddt,
          #               "interval"  :(tmp_enddt - tmp_startdt).seconds,
          #               # "start_node":tmp_node_id_list,
          #               # "end_node"  :end_node_list,
          #               # st&ed_nodeのみ変更
          #               "start_node":[tmp_node_id],
          #               "end_node"  :[data["nodelist"][num]["node_id"]],
          #               }
          #   data_lists_stay.append(se_data)
          #   break

          tmp_startdt = data['id']['get_time_no']
          start_nodelist = tmp_nodelist

        else:
          # tmp_node_id = data["nodelist"][0]["node_id"]
          # tmp_node_id_list = end_node_list
          # tmp_node_id = tmp_node_id_list[0]
          tmp_startdt = data['id']['get_time_no']
          start_nodelist = []
          for nodedata in data["nodelist"]:
            start_nodelist.append({"pcwl_id":convert_nodeid(nodedata['node_id']),"rssi":nodedata['dbm']})
          for num in range(0, min(len(data["nodelist"]), 3)):
            tmp_num = convert_nodeid(data["nodelist"][num]['node_id'])
            nodecnt_dict.update({tmp_num : nodecnt_dict[tmp_num]+1})

      else:
        tmp_mac = data["id"]["mac"]
        start_nodelist = []
        for nodedata in data["nodelist"]:
          start_nodelist.append({"pcwl_id":convert_nodeid(nodedata['node_id']),"rssi":nodedata['dbm']})

        data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
        tmp_startdt = data['id']['get_time_no']
        node_history = []

        node_history.append({"node":start_nodelist, "dt":data['id']['get_time_no']})
        nodecnt_dict ={}
        for num in range(MIN_NODE_NUM, MAX_NODE_NUM+1):
          nodecnt_dict.update({num:0})

      count_all += 1
      if count_all % 1000 == 0:
        end = time.time()
        print (count_all, end-start)
        start = time.time()

    data_lists = sorted(data_lists, key=lambda x:x["start_time"], reverse=True)
    data_lists_stay = sorted(data_lists_stay, key=lambda x:x["start_time"], reverse=True)
    data_lists_experiment = sorted(data_lists_experiment, key=lambda x:x["start_time"], reverse=True) # 実験用  

    # import time
    # start = time.time()
    # make_pfvinfo(data_lists)
    # make_stayinfo(data_lists_stay)
    # end = time.time()
    # print("time:"+str(end-start))

    ### 下記のコメントアウト解除でエラー発生 (2015年11月2日修正済み)###
    # make_pfvinfo(data_lists,db.pfvinfo)
    make_pfvinfo(data_lists_experiment,db.pfvinfoexperiment)
    # make_stayinfo(data_lists_stay,db.stayinfo)

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

def distance_filter(st_list,ed_list,interval):
  route_info = [] # 経路情報の取り出し
  if ed_list == []:
    return [[],[]]

  route_info += db.pcwlroute.find({"$and":[
                                            {"query" : st_list[0]["pcwl_id"]}, 
                                            {"query" : ed_list[0]["pcwl_id"]}
                                          ]})
  route_info = route_info[0]["dlist"]
  d_total = 0
  d_total_max = 0
  for route in route_info:
    for node in route:
      d_total += node["distance"]
    if (d_total > d_total_max):
      d_total_max = d_total
  if d_total_max < interval*20:
    return [st_list,ed_list]
  else :
    if (len(st_list)>=2) and (len(ed_list)>=2):
      if (st_list[1]["rssi"]) > (ed_list[1]["rssi"]):
        return distance_filter(st_list,ed_list[1:],interval)
      else :
        return distance_filter(st_list[1:],ed_list,interval)
    elif (len(st_list)>=2) and (len(ed_list)==1):
      return distance_filter(st_list[1:],ed_list,interval)
    elif (len(st_list)==1) and (len(ed_list)>=2):
      return distance_filter(st_list,ed_list[1:],interval)
    else :
      return [[],[]]
