# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
# from cms.forms import SensorForm
# from cms.models import Sensor2, Sensor3, initial_db, temp_db, error_db, pr_req
from pfv.models import pr_req, test, pcwlnode, tmpcol, pfvinfo, pfvinfoexperiment, pfvinfoexperiment2, pcwltime, stayinfo
from pfv.convert_nodeid import *
from pfv.save_pfvinfo import make_pfvinfo, make_pfvinfoexperiment
from pfv.make_pcwltime import make_pcwltime
from mongoengine import *
from pymongo import *
import requests

import json
import math
import datetime
import locale
from cms.convert_datetime import datetime_to_12digits, dt_from_str_to_iso, shift_time, dt_from_iso_to_str, dt_insert_partition_to_min, dt_from_iso_to_jap, dt_from_14digits_to_iso

# 今日の日付
d = datetime.datetime.today() # 2014-11-20 19:41:51.011593
dt = datetime.datetime.today() # 2014-11-20 19:41:51.011593
d = str(d.year)+("0"+str(d.month))[-2:]+("0"+str(d.day))[-2:]+("0"+str(d.hour))[-2:]+("0"+str(int(d.minute/5)*5))[-2:] # 201411201940

client = MongoClient()
db = client.nm4bd
db.test.create_index([("get_time_no", DESCENDING)])
db.pfvinfo.create_index([("datetime", ASCENDING)])
db.pfvinfoexperiment.create_index([("datetime", ASCENDING)])
db.stayinfo.create_index([("datetime", ASCENDING)])
db.pcwltime.create_index([("datetime", DESCENDING)])
db.pcwlroute.create_index([("query", ASCENDING)])

### データ登録方法 ###
# 1.http://127.0.0.1:8000/pfv/data_list/
# 2.http://127.0.0.1:8000/pfv/aggregate/
# 3.http://127.0.0.1:8000/pfv/analyze/
# 4.http://127.0.0.1:8000/pfv/get_start_end/
# 5.http://127.0.0.1:8000/pfv/pfv_map/

# データリスト画面 http://127.0.0.1:8000/pfv/data_list/  
def data_list(request, limit=100, date_time=d):
  dt = date_time + "00"
  
  # データベースから取り出し
  dataset = []
  # t = test.objects(get_time_no__lte=dt).order_by("-get_time_no").limit(int(limit))
  t = db.test.find({"get_time_no":{"$lte":dt}}).sort("get_time_no", DESCENDING).limit(int(limit))
  for data in t:
    data["node_id"] = convert_nodeid(data["node_id"])
    dataset.append(data)
  return render_to_response('pfv/data_list.html',  # 使用するテンプレート
                              {'t': dataset, 'limit':limit, 'year':date_time[0:4],'month':date_time[4:6],
                               'day':date_time[6:8],'hour':date_time[8:10],'minute':date_time[10:12]} )

# pfvマップ画面 http://localhost:8000/cms/pfv_map/
def pfv_map(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20150603122130')
  timerange = int(request.GET.get('timerange', 10))
  experiment = int(request.GET.get('experiment', 0))
  language = request.GET.get('language', 'jp')

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find()

  # pfv情報の取り出し
  pfvinfo = []
  if experiment == 1: # 実験データ
    pfvinfo += db.pfvinfoexperiment.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  elif experiment == 2: # 実験データ2
    pfvinfo += db.pfvinfoexperiment2.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  else : # 非実験データ
    pfvinfo += db.pfvinfo.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  if len(pfvinfo) >= 1:
    for i in range(1,len(pfvinfo)): # timerange内のpfv情報を合成
      for j in range(0,len(pfvinfo[i]["plist"])):
        pfvinfo[i]["plist"][j]["size"] += pfvinfo[i-1]["plist"][j]["size"]
        if (experiment == 1) or (experiment == 2): # 実験データ
          for mac in pfvinfo[i]["plist"][j]["mac_list"]:
            if mac not in pfvinfo[i-1]["plist"][j]["mac_list"]:
              pfvinfo[i-1]["plist"][j]["mac_list"] += [mac]
          pfvinfo[i]["plist"][j]["mac_list"] = pfvinfo[i-1]["plist"][j]["mac_list"]
    pfvinfo = pfvinfo[-1]["plist"]
  else :
    if experiment == 1: # 実験データ
      pfvinfo += db.pfvinfoexperiment.find().limit(1)
    if experiment == 2: # 実験データ2
      pfvinfo += db.pfvinfoexperiment2.find().limit(1)
    else : # 非実験データ
      pfvinfo += db.pfvinfo.find().limit(1)
    pfvinfo = pfvinfo[0]["plist"]
    for j in range(0,len(pfvinfo)):
      pfvinfo[j]["size"] = 0 


  # 滞留端末情報の取り出し
  stayinfo = []
  stayinfo += db.stayinfo.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  if len(stayinfo) >= 1:
    for i in range(1,len(stayinfo)):
      for j in range(0,len(stayinfo[i]["plist"])):
        stayinfo[i]["plist"][j]["size"] += stayinfo[i-1]["plist"][j]["size"]
        for mac in stayinfo[i]["plist"][j]["mac_list"]:
          if mac in stayinfo[i-1]["plist"][j]["mac_list"]:
            stayinfo[i]["plist"][j]["size"] -= 1
          else :
            stayinfo[i-1]["plist"][j]["mac_list"] += [mac]
        stayinfo[i]["plist"][j]["mac_list"] = stayinfo[i-1]["plist"][j]["mac_list"]
    stayinfo = stayinfo[-1]["plist"]

  # 滞留端末情報をPCWL情報にひも付け
  _pcwlnode_with_stayinfo = []
  for i in range(0,len(pcwlnode)):
    if len(stayinfo) >= 1:
      size = stayinfo[i]["size"]
    else :
      size = 0
    _pcwlnode_with_stayinfo.append({
      "pcwl_id":pcwlnode[i]["pcwl_id"],
      "pos_x":pcwlnode[i]["pos_x"],
      "pos_y":pcwlnode[i]["pos_y"],
      "size":size
      })
  
  return render_to_response('pfv/pfv_map.html',  # 使用するテンプレート
                              {'pcwlnode': _pcwlnode_with_stayinfo,'pfvinfo': pfvinfo,
                               'experiment':experiment,'language':language,'timerange':timerange,
                               'year':lt.year,'month':lt.month,'day':lt.day,
                               'hour':lt.hour,'minute':lt.minute,'second':lt.second} 
                              )

# pfvマップ用JSON
def pfv_map_json(request):  

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20150603122130')
  timerange = int(request.GET.get('timerange', 10))
  experiment = int(request.GET.get('experiment', 0))

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  # pfv情報の取り出し
  pfvinfo = []
  if experiment == 1: # 実験データ
    pfvinfo += db.pfvinfoexperiment.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  elif experiment == 2: # 実験データ2
    pfvinfo += db.pfvinfoexperiment.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  else : # 非実験データ
    pfvinfo += db.pfvinfo.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)  
  if len(pfvinfo) >= 1:
    for i in range(1,len(pfvinfo)): # timerange内のpfv情報を合成
      for j in range(0,len(pfvinfo[i]["plist"])):
        pfvinfo[i]["plist"][j]["size"] += pfvinfo[i-1]["plist"][j]["size"]
        if (experiment == 1) or (experiment == 2): # 実験データ
          for mac in pfvinfo[i]["plist"][j]["mac_list"]:
            if mac not in pfvinfo[i-1]["plist"][j]["mac_list"]:
              pfvinfo[i-1]["plist"][j]["mac_list"] += [mac]
          pfvinfo[i]["plist"][j]["mac_list"] = pfvinfo[i-1]["plist"][j]["mac_list"]
    pfvinfo = pfvinfo[-1]["plist"]  

  # 滞留端末情報の取り出し
  stayinfo = []
  stayinfo += db.stayinfo.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  if len(stayinfo) >= 1:
    for i in range(1,len(stayinfo)):
      for j in range(0,len(stayinfo[i]["plist"])):
        stayinfo[i]["plist"][j]["size"] += stayinfo[i-1]["plist"][j]["size"]
        for mac in stayinfo[i]["plist"][j]["mac_list"]:
          if mac in stayinfo[i-1]["plist"][j]["mac_list"]:
            stayinfo[i]["plist"][j]["size"] -= 1
          else :
            stayinfo[i-1]["plist"][j]["mac_list"] += [mac]
        stayinfo[i]["plist"][j]["mac_list"] = stayinfo[i-1]["plist"][j]["mac_list"]
    stayinfo = stayinfo[-1]["plist"]

  dataset = {"pfvinfo":pfvinfo,"stayinfo":stayinfo}
  return render_json_response(request, dataset) # dataをJSONとして出力

# JSON出力
def render_json_response(request, data, status=None): # response を JSON で返却
  
  json_str = json.dumps(data, ensure_ascii=False, indent=2)
  callback = request.GET.get('callback')
  if not callback:
      callback = request.REQUEST.get('callback')  # POSTでJSONPの場合
  if callback:
      json_str = "%s(%s)" % (callback, json_str)
      response = HttpResponse(json_str, content_type='application/javascript; charset=UTF-8', status=status)
  else:
      response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
  return response

# pfvグラフ
def pfv_graph(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20150603122130')
  direction = request.GET.get('direction', '2205')
  experiment = int(request.GET.get('experiment', 0))
  language = request.GET.get('language', 'jp')

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(hours = 1) # 1時間前までのデータを取得 

  st = int(direction[0:2])
  ed = int(direction[2:4])

  # pfv情報の取り出しとグラフデータ化
  pfvinfo_list = []
  pfvgraph_info = []
  if experiment == 1: # 実験データ
    pfvinfo_list += db.pfvinfoexperiment.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  if experiment == 2: # 実験データ2
    pfvinfo_list += db.pfvinfoexperiment2.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  else : # 非実験データ
    pfvinfo_list += db.pfvinfo.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  if len(pfvinfo_list) >= 1:
    for i in range(0,len(pfvinfo_list[0]["plist"])):
      if (pfvinfo_list[0]["plist"][i]["direction"][0] == st) and (pfvinfo_list[0]["plist"][i]["direction"][1] == ed):
        num = i
    for pfvinfo in pfvinfo_list:
      pfvgraph_info.append({"datetime":pfvinfo["datetime"],"size":pfvinfo["plist"][num]["size"]})

  return render_to_response('pfv/pfv_graph.html',  # 使用するテンプレート
                              {'pfvgraph_info': pfvgraph_info, 'experiment':experiment
                              ,'start_node':st, 'end_node':ed, 'language':language
                              ,'year':lt.year,'month':lt.month,'day':lt.day
                              ,'hour':lt.hour,'minute':lt.minute,'second':lt.second} 
                              )

# stayグラフ
def stay_graph(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20150603122130')
  node = int(request.GET.get('node', 1))
  language = request.GET.get('language', 'jp')

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(hours = 1) # 1時間前までのデータを取得 

  # 滞留端末情報の取り出しとグラフデータ化
  stayinfo_list = []
  staygraph_info = []
  stayinfo_list += db.stayinfo.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  if len(stayinfo_list) >= 1:
    for i in range(0,len(stayinfo_list[0]["plist"])):
      if stayinfo_list[0]["plist"][i]["pcwl_id"] == node:
        num = i
    for stayinfo in stayinfo_list:
      staygraph_info.append({"datetime":stayinfo["datetime"],"size":stayinfo["plist"][num]["size"]})

  return render_to_response('pfv/stay_graph.html',  # 使用するテンプレート
                              {'staygraph_info': staygraph_info, 'node':int(node), 'language':language
                              ,'year':lt.year,'month':lt.month,'day':lt.day
                              ,'hour':lt.hour,'minute':lt.minute,'second':lt.second} 
                              )

  # pfvマップ画面 http://localhost:8000/cms/pfv_heatmap/
def pfv_heatmap(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20150603122130')
  timerange = int(request.GET.get('timerange', 10))
  experiment = int(request.GET.get('experiment', 0))
  language = request.GET.get('language', 'jp')

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find()

  # pfv情報の取り出し
  pfvinfo = []
  if experiment == 1: # 実験データ
    pfvinfo += db.pfvinfoexperiment.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  elif experiment == 2: # 実験データ2
    pfvinfo += db.pfvinfoexperiment2.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  else : # 非実験データ
    pfvinfo += db.pfvinfo.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  if len(pfvinfo) >= 1:
    for i in range(1,len(pfvinfo)): # timerange内のpfv情報を合成
      for j in range(0,len(pfvinfo[i]["plist"])):
        pfvinfo[i]["plist"][j]["size"] += pfvinfo[i-1]["plist"][j]["size"]
        if (experiment == 1) or (experiment == 2): # 実験データ
          for mac in pfvinfo[i]["plist"][j]["mac_list"]:
            if mac not in pfvinfo[i-1]["plist"][j]["mac_list"]:
              pfvinfo[i-1]["plist"][j]["mac_list"] += [mac]
          pfvinfo[i]["plist"][j]["mac_list"] = pfvinfo[i-1]["plist"][j]["mac_list"]
    pfvinfo = pfvinfo[-1]["plist"]
  else :
    if experiment == 1: # 実験データ
      pfvinfo += db.pfvinfoexperiment.find().limit(1)
    if experiment == 2: # 実験データ2
      pfvinfo += db.pfvinfoexperiment2.find().limit(1)
    else : # 非実験データ
      pfvinfo += db.pfvinfo.find().limit(1)
    pfvinfo = pfvinfo[0]["plist"]
    for j in range(0,len(pfvinfo)):
      pfvinfo[j]["size"] = 0 


  # 滞留端末情報の取り出し
  stayinfo = []
  stayinfo += db.stayinfo.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  if len(stayinfo) >= 1:
    for i in range(1,len(stayinfo)):
      for j in range(0,len(stayinfo[i]["plist"])):
        stayinfo[i]["plist"][j]["size"] += stayinfo[i-1]["plist"][j]["size"]
        for mac in stayinfo[i]["plist"][j]["mac_list"]:
          if mac in stayinfo[i-1]["plist"][j]["mac_list"]:
            stayinfo[i]["plist"][j]["size"] -= 1
          else :
            stayinfo[i-1]["plist"][j]["mac_list"] += [mac]
        stayinfo[i]["plist"][j]["mac_list"] = stayinfo[i-1]["plist"][j]["mac_list"]
    stayinfo = stayinfo[-1]["plist"]

  # 滞留端末情報をPCWL情報にひも付け
  _pcwlnode_with_stayinfo = []
  for i in range(0,len(pcwlnode)):
    if len(stayinfo) >= 1:
      size = stayinfo[i]["size"]
    else :
      size = 0
    _pcwlnode_with_stayinfo.append({
      "pcwl_id":pcwlnode[i]["pcwl_id"],
      "pos_x":pcwlnode[i]["pos_x"],
      "pos_y":pcwlnode[i]["pos_y"],
      "size":size
      })
  
  return render_to_response('pfv/pfv_heatmap.html',  # 使用するテンプレート
                              {'pcwlnode': _pcwlnode_with_stayinfo,'pfvinfo': pfvinfo,
                               'experiment':experiment,'language':language,'timerange':timerange,
                               'year':lt.year,'month':lt.month,'day':lt.day,
                               'hour':lt.hour,'minute':lt.minute,'second':lt.second} 
                              )