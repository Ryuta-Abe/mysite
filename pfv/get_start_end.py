# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test, tmpcol, pcwlroute
from pfv.save_pfvinfo import make_pfvinfo, make_stayinfo
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
  # make_pcwltime()
  import time
  start = time.time()
  from datetime import datetime, timedelta
  tmp_mac     = ""
  tmp_startdt = datetime(2000, 1, 1, 0, 0, 0)
  data_lists = []
  data_lists_stay = []
  count = 0
  count_all = 0

  # 6F実験で用いた端末のMACリスト
  mac_list_experiment = ["90:b6:86:52:77:2a","80:be:05:6c:6b:2b","98:e0:d9:35:92:4d","18:cf:5e:4a:3a:17","18:00:2d:62:6c:d1"]
  data_lists_experiment = []
  node_history = []
  end_nodelist = []

  # datas = db.tmpcol.find({"_id.get_time_no":{"$gte":20150925173500,"$lte":20150925182000}}).limit(5000).sort("_id.get_time_no",-1).sort("_id.mac")

  ### 処理が重いため、実装時はlimitをつける ###
  datas = db.tmpcol.find().sort("_id.get_time_no",-1).sort("_id.mac")

  for data in datas:
    data['id'] = data['_id']

    # macaddrが一致するものを処理
    if (data["id"]["mac"] == tmp_mac):
      data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
      data['nodelist'] = sorted(data['nodelist'], key=lambda x:x["dbm"], reverse=True)
      # end_node_list = []
      # node_id変換
      # for list_data in data["nodelist"]:
        # list_data['node_id'] = convert_nodeid(list_data['node_id'])
        # end_node_list.append(convert_nodeid(list_data["node_id"]))

      # intervalによる除外
      if ((data['id']['get_time_no'] - tmp_startdt).seconds <= 60):
        tmp_enddt = data['id']['get_time_no']
        del(data['_id'])

        # 行き来する端末除外
        repeat_cnt = 0
        tmp_nodelist = []
        for nodedata in data["nodelist"]:
          tmp_nodelist.append({"pcwl_id":convert_nodeid(nodedata['node_id']),"rssi":nodedata['dbm']})
          # tmp_nodelist.append(nodedata['node_id'])

        node_history.append({"node":tmp_nodelist, "dt":data['id']['get_time_no']})

        # PFVのデータリスト生成
        node_cnt = min(len(data["nodelist"]), 5)
        for num in range(0, node_cnt):
          for histoy in node_history:
            repeat_cnt = 0
            if not(data['id']['get_time_no'] - timedelta(minutes=5) <= histoy["dt"] <= data['id']['get_time_no'] + timedelta(minutes=5)):
              node_history.remove(histoy)
            else:
              if (data["nodelist"][num]["node_id"] in histoy["node"]):
                repeat_cnt += 1

        interval = (tmp_enddt - tmp_startdt).seconds
        [st_list,ed_list] = distance_filter(tmp_nodelist, end_nodelist, interval)
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
        #     if repeat_cnt <= 60:
        #       data_lists.append(se_data)
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

    else:
      tmp_mac = data["id"]["mac"]
      # end_node_list = []
      end_nodelist = []
      # for node in data["nodelist"]:
      # tmp_nodelist = []
      for nodedata in data["nodelist"]:
        end_nodelist.append({"pcwl_id":convert_nodeid(nodedata['node_id']),"rssi":nodedata['dbm']})
        # end_node_list.append(convert_nodeid(node["node_id"]))
        # start_node_list.append(convert_nodeid(node["node_id"]))

      data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
      tmp_startdt = data['id']['get_time_no']
      node_history = []

      node_history.append({"node":end_nodelist, "dt":data['id']['get_time_no']})

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
  # make_pfvinfo(data_lists_experiment,db.pfvinfoexperiment)

  return render_to_response('pfv/get_start_end.html',  # 使用するテンプレート
                              {"datas":data_lists_experiment[:2000], "count":count, "count_all":count_all} 
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
