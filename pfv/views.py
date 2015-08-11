# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
# from cms.forms import SensorForm
# from cms.models import Sensor2, Sensor3, initial_db, temp_db, error_db, pr_req
from pfv.models import pr_req, test
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

