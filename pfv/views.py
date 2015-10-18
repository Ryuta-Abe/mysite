# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
# from cms.forms import SensorForm
# from cms.models import Sensor2, Sensor3, initial_db, temp_db, error_db, pr_req
from pfv.models import pr_req, test, pcwlnode, tmpcol, pfvinfo, pcwltime
from pfv.convert_nodeid import *
from pfv.save_pfvinfo import make_pfvinfo, make_pfvinfo_experiment
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
  dt = int(date_time + "00")
  
  # データベースから取り出し
  t = test.objects(get_time_no__lte=dt).order_by("-get_time_no").limit(int(limit))

  return render_to_response('pfv/data_list.html',  # 使用するテンプレート
                              {'t': t, 'limit':limit, 'year':date_time[0:4],'month':date_time[4:6],
                               'day':date_time[6:8],'hour':date_time[8:10],'minute':date_time[10:12]} )

# pfvマップ画面 http://localhost:8000/cms/pfv_map/
def pfv_map(request, date_time=999, timerange=10):
  import time
  # lt = datetime.datetime.today()
  # lt = datetime.datetime(2015,6,3,12,10,30)
  lt = datetime.datetime(2015,9,25,18,20,30)
  gt = lt - datetime.timedelta(seconds = int(timerange)) # timerange秒前までのデータを取得

  # pcwl情報の取り出し
  _pcwlnode = []
  _pcwlnode += pcwlnode.objects()

  # pfv情報の取り出し
  # start = time.time()
  _pfvinfo = []
  _pfvinfo += db.pfvinfo.find({"datetime":{"$gte":gt, "$lte":lt}}).sort("datetime", ASCENDING)
  # end = time.time()
  # print("Time:"+str(end - start))

  if len(_pfvinfo) >= 1:
    for i in range(1,len(_pfvinfo)): # timerange内のpfv情報を合成
      for j in range(0,len(_pfvinfo[i]["plist"])):
        _pfvinfo[i]["plist"][j]["size"] += _pfvinfo[i-1]["plist"][j]["size"]
    _pfvinfo = _pfvinfo[-1]["plist"]

  # 滞留端末情報の取り出し
  _stayinfo = []
  # DBを未作成なので適当な値
  s1 = []
  s2 = []
  # 時間s1の滞留データ
  s1.append({"pcwl_id":1,"size":3,"mac_list":["a","b","c"]})
  s1.append({"pcwl_id":2,"size":1,"mac_list":["d"]})
  s1.append({"pcwl_id":3,"size":2,"mac_list":["e","f"]})
  s1.append({"pcwl_id":4,"size":3,"mac_list":["g","h","i"]})
  for i in range(5,25):
    s1.append({"pcwl_id":i,"size":0,"mac_list":[]})
  s1.append({"pcwl_id":27,"size":3,"mac_list":["x","y","z"]})
  # 時間s2の滞留データ
  s2.append({"pcwl_id":1,"size":4,"mac_list":["a","b","d","e"]})
  s2.append({"pcwl_id":2,"size":0,"mac_list":[]})
  s2.append({"pcwl_id":3,"size":3,"mac_list":["f","b","g"]})
  s2.append({"pcwl_id":4,"size":2,"mac_list":["j","k"]})
  for i in range(5,25):
    s2.append({"pcwl_id":i,"size":0,"mac_list":[]})
  s2.append({"pcwl_id":27,"size":3,"mac_list":["x","y","z"]})

  _stayinfo = [s1]
  # 適当な値ここまで

  # 複数の滞留端末情報の合成
  if len(_pfvinfo) >= 1:
    for i in range(1,len(_stayinfo)):
      for j in range(0,len(_stayinfo[i])):
        _stayinfo[i][j]["size"] += _stayinfo[i-1][j]["size"]
        for mac in _stayinfo[i][j]["mac_list"]:
          if mac in _stayinfo[i-1][j]["mac_list"]:
            _stayinfo[i][j]["size"] -= 1
          else :
            _stayinfo[i-1][j]["mac_list"] += [mac]
        _stayinfo[i][j]["mac_list"] = _stayinfo[i-1][j]["mac_list"]
    _stayinfo = _stayinfo[-1]
  # _stayinfo = _stayinfo[0]

  # 滞留端末情報をPCWL情報にひも付け
  _pcwlnode_with_stayinfo = []
  for i in range(0,len(_pcwlnode)):
    # if (type(_stayinfo[i]["size"])==str):
    #   pass
    print(_stayinfo)
    # print(len(_pcwlnode))
    # print(i)
    _pcwlnode_with_stayinfo.append({
      "pcwl_id":_pcwlnode[i]["pcwl_id"],
      "pos_x":_pcwlnode[i]["pos_x"],
      "pos_y":_pcwlnode[i]["pos_y"],
      "size":_stayinfo[i]["size"]
      })
  
  return render_to_response('pfv/pfv_map.html',  # 使用するテンプレート
                              {'pcwlnode': _pcwlnode_with_stayinfo,'pfvinfo': _pfvinfo,
                               'year':lt.year,'month':lt.month,'day':lt.day,
                               'hour':lt.hour,'minute':lt.minute,'second':lt.second} 
                              )

# pfvマップ用JSON
def pfv_map_json(request, date_time=999, timerange=10):  

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = int(timerange)) # timerange秒前までのデータを取得

  # pfv情報の取り出し
  _pfvinfo = []
  _pfvinfo += pfvinfo.objects(datetime__gt = gt, datetime__lt = lt)
  if len(_pfvinfo) >= 1:
    for i in range(1,len(_pfvinfo)): # timerange内のpfv情報を合成
      for j in range(0,len(_pfvinfo[i]["plist"])):
        _pfvinfo[i]["plist"][j]["size"] += _pfvinfo[i-1]["plist"][j]["size"]
    _pfvinfo = _pfvinfo[-1]["plist"]

  # 滞留端末情報の取り出し
  _stayinfo = []
  s1 = []
  s2 = []

  s1.append({"pcwl_id":1,"size":3,"mac_list":["a","b","c"]})
  s1.append({"pcwl_id":2,"size":1,"mac_list":["d"]})
  s1.append({"pcwl_id":3,"size":2,"mac_list":["e","f"]})
  s1.append({"pcwl_id":4,"size":3,"mac_list":["g","h","i"]})
  for i in range(5,25):
    s1.append({"pcwl_id":i,"size":0,"mac_list":[]})
  s1.append({"pcwl_id":27,"size":3,"mac_list":["x","y","z"]})

  s2.append({"pcwl_id":1,"size":4,"mac_list":["a","b","d","e"]})
  s2.append({"pcwl_id":2,"size":0,"mac_list":[]})
  s2.append({"pcwl_id":3,"size":3,"mac_list":["f","b","g"]})
  s2.append({"pcwl_id":4,"size":2,"mac_list":["j","k"]})
  for i in range(5,25):
    s2.append({"pcwl_id":i,"size":0,"mac_list":[]})
  s2.append({"pcwl_id":27,"size":3,"mac_list":["x","y","z"]})

  _stayinfo = [s1,s2]

  # 複数の対流端末情報の合成
  if len(_pfvinfo) >= 1:
    for i in range(1,len(_stayinfo)):
      for j in range(0,len(_stayinfo[i])):
        _stayinfo[i][j]["size"] += _stayinfo[i-1][j]["size"]
        for mac in _stayinfo[i][j]["mac_list"]:
          if mac in _stayinfo[i-1][j]["mac_list"]:
            _stayinfo[i][j]["size"] -= 1
          else :
            _stayinfo[i-1][j]["mac_list"] += [mac]
        _stayinfo[i][j]["mac_list"] = _stayinfo[i-1][j]["mac_list"]
    _stayinfo = _stayinfo[-1]

  dataset = {"pfvinfo":_pfvinfo,"stayinfo":_stayinfo}
  print(_stayinfo)
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
def pfv_graph(request, date_time=999, direction="2205"):

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(hours = 1) # 1時間前までのデータを取得 

  # DBクエリ指定テスト
  st = int(direction[0:2])
  ed = int(direction[2:4])
  _pfvinfo_list = []
  _pfvinfo_list += pfvinfo.objects(datetime__gt = gt, datetime__lt = lt)
  for i in range(0,len(_pfvinfo_list[0]["plist"])):
    if (_pfvinfo_list[0]["plist"][i]["direction"][0] == st) and (_pfvinfo_list[0]["plist"][i]["direction"][1] == ed):
      num = i
  pfvgraph_info = []
  for _pfvinfo in _pfvinfo_list:
    pfvgraph_info.append({"datetime":_pfvinfo["datetime"],"size":_pfvinfo["plist"][num]["size"]})

  return render_to_response('pfv/pfv_graph.html',  # 使用するテンプレート
                              {'pfvgraph_info': pfvgraph_info, 'start_node':st, 'end_node':ed
                              ,'year':lt.year,'month':lt.month,'day':lt.day
                              ,'hour':lt.hour,'minute':lt.minute,'second':lt.second} 
                              )
