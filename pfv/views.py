# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
# from cms.forms import SensorForm
# from cms.models import Sensor2, Sensor3, initial_db, temp_db, error_db, pr_req
from pfv.models import pr_req, test, pcwlnode, tmpcol, pfvinfo, pcwltime
from pfv.convert_nodeid import *
from pfv.save_pfvinfo import make_pfvinfo, make_pfvinfo_experiment
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
d = str(d.year)+("0"+str(d.month))[-2:]+("0"+str(d.day))[-2:]+("0"+str(d.hour))[-2:]+("0"+str(int(d.minute/5)*5))[-2:] # 201411201940

client = MongoClient()
db = client.nm4bd

# データリスト画面 http://localhost:8000/cms/data_list/
def data_list(request, limit=100, date_time=d):
  from datetime import datetime
 
  # 日付をstr12桁に合わせる --> 2014-11-20 19:40
  date_time = datetime_to_12digits(date_time)

  # データベースから取り出し
  t = test.objects(get_time_no__lte=20150603071300).order_by("-get_time_no").limit(100)
  ag = test._get_collection().aggregate([
                                          # {"$limit":1000},
                                          {"$group":
                                            {"_id":
                                              {"get_time_no":"$get_time_no",}
                                            },
                                          },
                                          {"$out": "tmppcwltime"},
                                        ],
                                      allowDiskUse=True,
                                      # cursor={"batchSize":0}, useCursor=True,
                                      )
  jdatas = db.tmppcwltime.find()
  pcwltime.objects.all().delete()
  
  for jdata in jdatas:
    jdata['datetime'] = datetime.strptime(str(jdata['_id']['get_time_no']), '%Y%m%d%H%M%S')
    del(jdata['_id'])
    timedata = pcwltime(
                      datetime = jdata['datetime'],
                      )
    timedata.save()

  # ag = test._get_collection().aggregate([{"$match":{"node_id":1242}}])
  # ag2 = test._get_collection().aggregate([{"$group":{"_id":{"get_time_no":"$get_time_no"}, "count":{"$sum":1}}}])
  # t = test.objects(node_id=1244).limit(25000)
  # t = test.objects(get_time_no__gte=20150603114000).limit(1000)

  return render_to_response('pfv/data_list.html',  # 使用するテンプレート
                              {'t': t, 'limit':limit, 'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]} )

# pfvマップ画面 http://localhost:8000/cms/pfv_map/
def pfv_map(request, date_time=999, timerange=10):

  # lt = datetime.datetime.today()
  lt = datetime.datetime(2015,6,3,12,10,30)
  gt = lt - datetime.timedelta(seconds = int(timerange)) # timerange秒前までのデータを取得

  # pcwl情報の取り出し
  _pcwlnode = []
  _pcwlnode += pcwlnode.objects()

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

  # 滞留端末情報をPCWL情報にひも付け
  _pcwlnode_with_stayinfo = []
  for i in range(0,len(_pcwlnode)):
    _pcwlnode_with_stayinfo.append({
      "pcwl_id":_pcwlnode[i]["pcwl_id"],
      "pos_x":_pcwlnode[i]["pos_x"],
      "pos_y":_pcwlnode[i]["pos_y"],
      "size":_stayinfo[i]["size"]
      })
  
  return render_to_response('pfv/pfv_map.html',  # 使用するテンプレート
                              {'pcwlnode': _pcwlnode_with_stayinfo,'pfvinfo': _pfvinfo
                              ,'year':lt.year,'month':lt.month,'day':lt.day
                              ,'hour':lt.hour,'minute':lt.minute,'second':lt.second} 
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

def aggregate_data(request):
  ag = test._get_collection().aggregate([
                                          # {"$limit":1000},
                                          {"$group":
                                            {"_id":
                                              {"mac":"$mac", 
                                               "get_time_no":"$get_time_no",
                                              },
                                             "nodelist":{"$push":{"dbm":"$dbm", "node_id":"$node_id"}},
                                            },
                                          },
                                          {"$out": "tmpcol"},
                                        ],
                                      allowDiskUse=True,
                                      # cursor={"batchSize":0}, useCursor=True,
                                      )

  return render_to_response('pfv/aggregate_data.html',  # 使用するテンプレート
                              {} 
                            )

def analyze_direction(request):
  from datetime import datetime

  ag = db.tmpcol.find({"_id.get_time_no":{"$gte":20150925174000,"$lte":20150925181000}}).sort("_id.mac").sort("_id.get_time_no",-1)
  # ag = db.tmpcol.find({"_id.get_time_no":{"$lte":20150925183500}}).limit(10000).sort("_id.mac").sort("_id.get_time_no",-1)
  ana_list = []
  for jdata in ag:
    jdata['id'] = jdata['_id']
    jdata['id']['get_time_no'] = datetime.strptime(str(jdata['id']['get_time_no']), '%Y%m%d%H%M%S')
    jdata['nodelist'] = sorted(jdata['nodelist'], key=lambda x:x["dbm"], reverse=True)
    for list_data in jdata['nodelist']:
      list_data['node_id'] = convert_nodeid(list_data['node_id'])
    del(jdata['_id'])
    ana_list.append(jdata)
  return render_to_response('pfv/analyze_direction.html',  # 使用するテンプレート
                              {'ag': ana_list} 
                            )

def get_start_end(request):
  from datetime import datetime
  tmp_mac     = ""
  tmp_startdt = datetime(2000, 1, 1, 0, 0, 0)
  # tmp_node_id   = 0
  data_lists = []
  count = 0
  count_all = 0

  # 6F実験で用いた端末のMACリスト
  mac_list_experiment = ["90:b6:86:52:77:2a","80:be:05:6c:6b:2b","98:e0:d9:35:92:4d","18:cf:5e:4a:3a:17","18:00:2d:62:6c:d1"]
  data_lists_experiment = []

  # datas = db.tmpcol.find({"_id.get_time_no":{"$gte":20150925173500,"$lte":20150925182000}}).limit(5000).sort("_id.get_time_no",-1).sort("_id.mac")
  datas = db.tmpcol.find().sort("_id.get_time_no",-1).sort("_id.mac")
  # tmp = []
  # tmp += datas
  tmp_node_id = convert_nodeid(datas[0]['nodelist'][0]['node_id'])
  for data in datas:
    data['id'] = data['_id']

    if (data["id"]["mac"] == tmp_mac):
      # tmp_mac = data["id"]["mac"]
      # tmp_startdt = datetime(2000, 1, 1, 0, 0, 0)

      data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')

      data['nodelist'] = sorted(data['nodelist'], key=lambda x:x["dbm"], reverse=True)

      for list_data in data['nodelist']:
        list_data['node_id'] = convert_nodeid(list_data['node_id'])

      if ((data['id']['get_time_no'] - tmp_startdt).seconds  < 60):
        tmp_enddt   = data['id']['get_time_no']

        del(data['_id'])
        # data['nodelist'] = data['nodelist'][0]

        if (data["nodelist"][0]["node_id"] != tmp_node_id):
          pass

          se_data =  {"mac":data["id"]["mac"],
                      "start_time":tmp_startdt,
                      "end_time"  :tmp_enddt,
                      "interval"  :(tmp_enddt - tmp_startdt).seconds,
                      "start_node":tmp_node_id,
                      "end_node"  :data["nodelist"][0]["node_id"],
                      }

          # print(tmp_enddt - tmp_startdt)
          # if (se_data["start_node"] != 0):
          data_lists.append(se_data)
          if se_data["mac"] in mac_list_experiment:
            data_lists_experiment.append(se_data)
          count += 1
          
      tmp_node_id = data["nodelist"][0]["node_id"]
      tmp_startdt = data['id']['get_time_no']
      # else:
        # tmp_node_id = data["nodelist"][0]["node_id"]
        # tmp_startdt = data['id']['get_time_no']
        # tmp_node_id = 0

    else:
      tmp_mac = data["id"]["mac"]
      data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
      tmp_startdt = data['id']['get_time_no']
      # tmp_node_id = 0

    # data_lists.reverse()
    count_all += 1
  data_lists = sorted(data_lists, key=lambda x:x["start_time"], reverse=True)
  data_lists_experiment = sorted(data_lists_experiment, key=lambda x:x["start_time"], reverse=True)
    # data_lists.remove({"start_node":0})
  make_pfvinfo(data_lists)
  make_pfvinfo_experiment(data_lists_experiment)

  return render_to_response('pfv/get_start_end.html',  # 使用するテンプレート
                              {"datas":data_lists, "count":count, "count_all":count_all} 
                            )  