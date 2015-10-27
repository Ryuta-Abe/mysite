# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test, tmpcol, pcwlroute
from pfv.save_pfvinfo import make_pfvinfo, make_pfvinfoexperiment, make_stayinfo
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

  # datas = db.tmpcol.find({"_id.get_time_no":{"$gte":20150925173500,"$lte":20150925182000}}).limit(5000).sort("_id.get_time_no",-1).sort("_id.mac")
  datas = db.tmpcol.find().sort("_id.get_time_no",-1).sort("_id.mac")
  # datas = db.tmpcol.find({"_id.get_time_no":{"$gte":20150925173500}}).sort("_id.get_time_no",-1).sort("_id.mac")
  tmp_node_id_list = []
  for tmp_node_id in datas[0]['nodelist']:
    tmp_node_id_list.append(convert_nodeid(tmp_node_id['node_id']))
  tmp_node_id = tmp_node_id_list[0]

  for data in datas:
    data['id'] = data['_id']

    if (data["id"]["mac"] == tmp_mac):
      data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
      data['nodelist'] = sorted(data['nodelist'], key=lambda x:x["dbm"], reverse=True)
      end_node_list = []
      for end_node in data["nodelist"]:
        end_node_list.append(convert_nodeid(end_node["node_id"]))

      for list_data in data['nodelist']:

        list_data['node_id'] = convert_nodeid(list_data['node_id'])
      if ((data['id']['get_time_no'] - tmp_startdt).seconds < 60):
        tmp_enddt = data['id']['get_time_no']
        del(data['_id'])

        # 行き来する端末除外
        repeat_cnt = 0
        tmp_nodelist = []
        for nodedata in data["nodelist"]:
          tmp_nodelist.append(nodedata['node_id'])

        node_history.append({"node":tmp_nodelist, "dt":data['id']['get_time_no']})
        for histoy in node_history:
          if not(data['id']['get_time_no'] - timedelta(minutes=10) <= histoy["dt"] <= data['id']['get_time_no'] + timedelta(minutes=10)):
            node_history.remove(histoy)
          else:
            if (data["nodelist"][0]["node_id"] in histoy["node"]):
              repeat_cnt += 1

        # PFVのデータリスト生成
        if data["nodelist"][0]["node_id"] != tmp_node_id:

          route_info = [] # 経路情報の取り出し
          route_info += db.pcwlroute.find({"$and":[
                                                    {"query" : tmp_node_id}, 
                                                    {"query" : data["nodelist"][0]["node_id"]}
                                                  ]})

          d_total = 0
          tmp_d_total = 0
          interval = (tmp_enddt - tmp_startdt).seconds
          for info in route_info:
            # for part in route:
            for route in info["dlist"]:
              for part in route:
                pass
                tmp_d_total += part["distance"]
            if (tmp_d_total > d_total):
              d_total = tmp_d_total

          if d_total < interval*20:
            se_data =  {"mac":data["id"]["mac"],
                        "start_time":tmp_startdt,
                        "end_time"  :tmp_enddt,
                        "interval"  :(tmp_enddt - tmp_startdt).seconds,
                        "start_node":tmp_node_id_list,
                        "end_node"  :end_node_list,
                        }
            if repeat_cnt <= 4:
              data_lists.append(se_data)
              count += 1

            # 実験用
            if se_data["mac"] in mac_list_experiment:
              se_data["mac"] = name_filter(se_data["mac"])
              data_lists_experiment.append(se_data)

        # stayデータリスト生成
        elif data["nodelist"][0]["node_id"] == tmp_node_id:
          se_data =  {"mac":data["id"]["mac"],
                      "start_time":tmp_startdt,
                      "end_time"  :tmp_enddt,
                      "interval"  :(tmp_enddt - tmp_startdt).seconds,
                      "start_node":tmp_node_id_list,
                      "end_node"  :end_node_list,
                      }
          data_lists_stay.append(se_data)
          
      tmp_node_id_list = end_node_list
      tmp_node_id = tmp_node_id_list[0]
      tmp_startdt = data['id']['get_time_no']

    else:
      tmp_mac = data["id"]["mac"]
      data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
      tmp_startdt = data['id']['get_time_no']
      node_history = []
      tmp_nodelist = []
      for nodedata in data["nodelist"]:
        tmp_nodelist.append(nodedata['node_id'])

      node_history.append({"node":tmp_nodelist, "dt":data['id']['get_time_no']})

    count_all += 1

  data_lists = sorted(data_lists, key=lambda x:x["start_time"], reverse=True)
  data_lists_stay = sorted(data_lists_stay, key=lambda x:x["start_time"], reverse=True)
  data_lists_experiment = sorted(data_lists_experiment, key=lambda x:x["start_time"], reverse=True) # 実験用  

  # import time
  # start = time.time()
  # make_pfvinfo(data_lists)
  # make_stayinfo(data_lists_stay)
  # end = time.time()
  # print("time:"+str(end-start))
  # make_pfvinfoexperiment(data_lists_experiment)

  return render_to_response('pfv/get_start_end.html',  # 使用するテンプレート
                              {"datas":data_lists, "count":count, "count_all":count_all} 
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
