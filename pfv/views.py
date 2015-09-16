# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
# from cms.forms import SensorForm
# from cms.models import Sensor2, Sensor3, initial_db, temp_db, error_db, pr_req
from pfv.models import pr_req, test, pcwlnode
from mongoengine import *
from pymongo import *
import requests

import json
import math
import datetime
import locale

# from cms.convert_device_id    import convert_device_id
from cms.convert_datetime import datetime_to_12digits, dt_from_str_to_iso, shift_time, dt_from_iso_to_str, dt_insert_partition_to_min, dt_from_iso_to_jap
# from cms.convert_sensor_data    import convert_sensor_data

# from cms.write_to_mongo import write_to_initial_db, write_to_sensordb

# from cms.constmod import ConstClass

# 今日の日付
d = datetime.datetime.today() # 2014-11-20 19:41:51.011593
d = str(d.year)+("0"+str(d.month))[-2:]+("0"+str(d.day))[-2:]+("0"+str(d.hour))[-2:]+("0"+str(int(d.minute/5)*5))[-2:] # 201411201940

##- 外部ファイルをD3で読み込んで表示させる方法 -##
# 1.htmlファイルと読み込むファイル(.csv, .tsv, .jsonなど)を同じディレクトリに置く。
# 2.コマンドプロンプトを起動し、htmlファイルのあるディレクトリに移動する。
# 3.該当ディレクトリで　python -m http.server 8080 を入力。
# 4.ブラウザで http://localhost:8080/ にアクセス

# データリスト画面 http://localhost:8000/cms/data_list/
def data_list(request, limit=100, date_time=d):
 
  # 日付をstr12桁に合わせる --> 2014-11-20 19:40
  date_time = datetime_to_12digits(date_time)

  # データベースから取り出し
  # t = test.objects().limit(10000)
  # t = test.objects(node_id=1244).limit(25000)
  t = test.objects(get_time_no__gte=20150603114000).limit(1000)

  # for i in len(t):
  #   t[i]["get_time_no"] = str(t[i]["get_time_no"])[8:14]


  return render_to_response('pfv/data_list.html',  # 使用するテンプレート
                              {'t': t, 'limit':limit, 'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]} )

# pfvマップ画面 http://localhost:8000/cms/pfv_map/
def pfv_map(request, date_time=999):

  lt = datetime.datetime.today()

  # pcwl情報の取り出し
  _pcwlnode = []
  _pcwlnode += pcwlnode.objects()

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

  return render_to_response('cms/pfv_map.html'
  ,  # 使用するテンプレート
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

