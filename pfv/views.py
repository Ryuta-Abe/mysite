# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
# from cms.forms import SensorForm
# from cms.models import Sensor2, Sensor3, initial_db, temp_db, error_db, pr_req
from pfv.models import pr_req, test, pcwlnode, tmpcol
from pfv.convert_nodeid import *
from mongoengine import *
from pymongo import *
import requests

import json
import math
import datetime
import locale
from cms.convert_datetime import datetime_to_12digits, dt_from_str_to_iso, shift_time, dt_from_iso_to_str, dt_insert_partition_to_min, dt_from_iso_to_jap

# 今日の日付
d = datetime.datetime.today() # 2014-11-20 19:41:51.011593
d = str(d.year)+("0"+str(d.month))[-2:]+("0"+str(d.day))[-2:]+("0"+str(d.hour))[-2:]+("0"+str(int(d.minute/5)*5))[-2:] # 201411201940

client = MongoClient()
db = client.nm4bd

# データリスト画面 http://localhost:8000/cms/data_list/
def data_list(request, limit=100, date_time=d):
 
  # 日付をstr12桁に合わせる --> 2014-11-20 19:40
  date_time = datetime_to_12digits(date_time)

  # データベースから取り出し
  t = test.objects().limit(100)
  ag = test._get_collection().aggregate([{"$match":{"node_id":1242}}])
  ag2 = test._get_collection().aggregate([{"$group":{"_id":{"get_time_no":"$get_time_no"}, "count":{"$sum":1}}}])
  # t = test.objects(node_id=1244).limit(25000)
  # t = test.objects(get_time_no__gte=20150603114000).limit(1000)

  return render_to_response('pfv/data_list.html',  # 使用するテンプレート
                              {'t': t, 'limit':limit, 'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]} )

# pfvマップ画面 http://localhost:8000/cms/pfv_map/
def pfv_map(request, date_time=999):

  lt = datetime.datetime.today()

  # pcwl情報の取り出し
  _pcwlnode = []
  _pcwlnode += pcwlnode.objects()

  n_id = convert_nodeid(1240)
  ag = test._get_collection().aggregate([{"$group":{"_id":{"mac":"$mac", "get_time_no":"$get_time_no"}, "count":{"$sum":1}}}])

  # pfv情報の取り出し
  import random
  _pfvinfo = []

  _pfvinfo.append({'direction':[1,2],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[2,3],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[3,4],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[4,5],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[5,6],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[6,7],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[6,23],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[5,22],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[7,8],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[8,27],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[27,9],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[9,10],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[10,11],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[20,22],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[8,24],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[24,16],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[9,12],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[13,12],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[12,14],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[14,15],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[15,16],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[16,17],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[17,18],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[18,19],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[19,20],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[20,21],'size':random.randint(0, 10),'datetime':lt})

  _pfvinfo.append({'direction':[2,1],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[3,2],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[4,3],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[5,4],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[6,5],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[7,6],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[8,7],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[23,6],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[22,5],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[27,8],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[9,27],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[10,9],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[11,10],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[22,20],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[24,8],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[16,24],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[12,9],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[12,13],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[14,12],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[15,14],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[16,15],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[17,16],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[18,17],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[19,18],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[20,19],'size':random.randint(0, 10),'datetime':lt})
  _pfvinfo.append({'direction':[21,20],'size':random.randint(0, 10),'datetime':lt})

  return render_to_response('pfv/pfv_map.html',  # 使用するテンプレート
                              {'pcwlnode': _pcwlnode, 'pfvinfo': _pfvinfo, 'year':lt.year,'month':lt.month
                              ,'day':lt.day,'hour':lt.hour,'minute':lt.minute} 
                              )

# pfvマップ用JSON
def pfv_map_json(request, date_time=999):

  lt = datetime.datetime.today()

  # pfv情報の取り出し
  import random
  _pfvinfo = []

  _pfvinfo.append({'direction':[1,2],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[2,3],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[3,4],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[4,5],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[5,6],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[6,7],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[6,23],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[5,22],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[7,8],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[8,27],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[27,9],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[9,10],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[10,11],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[20,22],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[8,24],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[24,16],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[9,12],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[13,12],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[12,14],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[14,15],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[15,16],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[16,17],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[17,18],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[18,19],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[19,20],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[20,21],'size':random.randint(0, 10)})

  _pfvinfo.append({'direction':[2,1],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[3,2],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[4,3],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[5,4],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[6,5],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[7,6],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[8,7],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[23,6],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[22,5],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[27,8],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[9,27],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[10,9],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[11,10],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[22,20],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[24,8],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[16,24],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[12,9],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[12,13],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[14,12],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[15,14],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[16,15],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[17,16],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[18,17],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[19,18],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[20,19],'size':random.randint(0, 10)})
  _pfvinfo.append({'direction':[21,20],'size':random.randint(0, 10)})
  
  return render_json_response(request, _pfvinfo) # dataをJSONとして出力

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

def aggregate_data(request):
  # ag = db.command("test")
  # ag = db.test.runCommand()
  # ag = test._get_collection().aggregate([{"$group":{"_id":{"node_id":"$node_id"}, "count":{"$sum":1}}}])["result"]
  ag = test._get_collection().aggregate([
                                          # {"$limit":1000},
                                          {"$group":
                                            {"_id":
                                             # "mac":{"$push":"$mac"},
                                             # "get_time_no":{"$push":"$get_time_no"},
                                              {"mac":"$mac", 
                                               "get_time_no":"$get_time_no",
                                              },
                                             "nodelist":{"$push":{"dbm":"$dbm", "node_id":"$node_id"}},
                                            },
                                          },
                                          {"$out": "tmpcol"},
                                        ],
                                      allowDiskUse=True,
                                      # cursor={"batchSize":0},
                                      # useCursor=True,
                                      # explain=True
                                      )

  return render_to_response('pfv/aggregate_data.html',  # 使用するテンプレート
                              {} 
                            )

def analyze_direction(request):
  from datetime import datetime

  ag = db.tmpcol.find({"_id.get_time_no":{"$lte":20150603122000}}).limit(5000).sort("_id.mac").sort("_id.get_time_no",-1)
  ana_list = []
  for jdata in ag:
    # mac         = jdata["_id"]["mac"]
    jdata['id'] = jdata['_id']
    jdata['id']['get_time_no'] = datetime.strptime(str(jdata['id']['get_time_no']), '%Y%m%d%H%M%S')
    jdata['nodelist'] = sorted(jdata['nodelist'], key=lambda x:x["dbm"], reverse=True)
    for list_data in jdata['nodelist']:
      pass
      list_data['node_id'] = convert_nodeid(list_data['node_id'])
    del(jdata['_id'])
    ana_list.append(jdata)
    # get_time_no = jdata["_id"]["get_time_no"]
    # nodelist    = jdata["nodelist"]
  return render_to_response('pfv/analyze_direction.html',  # 使用するテンプレート
                              {'ag': ana_list} 
                            )