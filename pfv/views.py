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
def pfv_map(request, date_time=999, type="20"):

  lt = datetime.datetime.today()

  # pcwl情報の取り出し
  _pcwlnode = []
  _pcwlnode += pcwlnode.objects()

  # pfv情報の取り出し
  _pfvinfo = []
  _pfvinfo.append({'direction':[1,2],'size':5,'datetime':lt})
  _pfvinfo.append({'direction':[2,3],'size':4,'datetime':lt})
  _pfvinfo.append({'direction':[3,4],'size':4,'datetime':lt})
  _pfvinfo.append({'direction':[4,5],'size':3,'datetime':lt})
  _pfvinfo.append({'direction':[5,6],'size':5,'datetime':lt})
  _pfvinfo.append({'direction':[6,7],'size':7,'datetime':lt})
  _pfvinfo.append({'direction':[6,23],'size':2,'datetime':lt})
  _pfvinfo.append({'direction':[5,22],'size':4,'datetime':lt})
  _pfvinfo.append({'direction':[7,8],'size':9,'datetime':lt})
  _pfvinfo.append({'direction':[20,22],'size':4,'datetime':lt})
  _pfvinfo.append({'direction':[2,1],'size':0,'datetime':lt})
  _pfvinfo.append({'direction':[3,2],'size':1,'datetime':lt})
  _pfvinfo.append({'direction':[4,3],'size':1,'datetime':lt})
  _pfvinfo.append({'direction':[5,4],'size':2,'datetime':lt})
  _pfvinfo.append({'direction':[6,5],'size':2,'datetime':lt})
  _pfvinfo.append({'direction':[7,6],'size':3,'datetime':lt})
  _pfvinfo.append({'direction':[8,7],'size':6,'datetime':lt})
  _pfvinfo.append({'direction':[23,6],'size':0,'datetime':lt})
  _pfvinfo.append({'direction':[22,5],'size':3,'datetime':lt})
  _pfvinfo.append({'direction':[22,20],'size':3,'datetime':lt})

  return render_to_response('cms/pfv_map.html'
  ,  # 使用するテンプレート
                              {'pcwlnode': _pcwlnode, 'pfvinfo': _pfvinfo, 'year':lt.year,'month':lt.month
                              ,'day':lt.day,'hour':lt.hour,'minute':lt.minute} 
                              )

