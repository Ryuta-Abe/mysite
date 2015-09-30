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

def XXX(request):
  result ={}
  start_time = datetime.datetime(2014,11,10,11,10,40)
  end_time =  datetime.datetime(2014,11,10,11,11,19)
  distance = 40
  ab_time = end_time - start_time
  time = ab_time.total_seconds()
  d_t = distance / time
  time_list = [start_time,
  datetime.datetime(2014,11,10,11,10,49),
  datetime.datetime(2014,11,10,11,10,59),
  datetime.datetime(2014,11,10,11,11,9),
  end_time]
  node_d = [20, 5, 15]
  mod_d = 0
  mod_k = 0
  j = 0
  for i in range(1, len(time_list)):
    result["datetime"] = time_list[i]
    sa = time_list[i] - time_list[i-1]
    sabun =sa.total_seconds()
    kyori = sabun * d_t
    if mod_d == 0:
      if node_d[j] >= kyori:
        #size +1
        a = "first"
        mod_d = node_d[j] - kyori
        if mod_d == 0:
          j = j + 1
        else: break
      else:
        mod_k = kyori - node_d[j]
        j = j + 1
        if node_d[j] >= mod_k:
          #size + round(mod_k / kyori, 1)
          #size + round(node_d[j-1] / kyori, 1)
          b = "second"
          if mod_k == node_d[j]:
            j = j + 1
        else:
          mod_k = mod_k - node_d[j]
          j = j + 1
          if node_d[j] >= mod_k:
          #size + round(mod_k / kyori, 1)
          #size + round(node_d[j-1] / kyori, 1)
          #size + round(node_d[j-2] / kyori, 1)
            c = "third"
            if mod_k == 0:
              j= j + 1
            else: break
    else:
      if mod_d >= kyori:
        mod_d = mod_d - kyori
        #size + 1
        d = "fourth"
        if mod_d == 0:
          j = j + 1
      else:
        mod_k = kyori - mod_d
        j = j + 1
        if node_d[j] >= mod_k:
          #size + round(mod_k / kyori, 1)
          #size + round(mod_d / kyori, 1)
          e = "fifth"
          if mod_k == 0:
            j = j + 1
          else: break
        else:
          mod_k = mod_k - node_d[j]
          j = j + 1
          if node_d[j] >= mod_k:
          #size + round(mod_k / kyori, 1)
          #size + round(node_d[j-1] / kyori, 1)
          #size + round(mod_d / kyori, 1)
            f = "sixth"
            if mod_k == 0:
              j= j + 1
            else: break








  # ag = db.tmpcol.find({"_id.get_time_no":{"$lte":20150603122000}}).limit(100).sort("_id.mac").sort("_id.get_time_no",-1)
  # ana_list = []
  # for jdata in ag:
  #   # mac         = jdata["_id"]["mac"]
  #   jdata['id'] = jdata['_id']
  #   jdata['id']['get_time_no'] = datetime.strptime(str(jdata['id']['get_time_no']), '%Y%m%d%H%M%S')
  #   jdata['nodelist'] = sorted(jdata['nodelist'], key=lambda x:x["dbm"], reverse=True)
  #   for list_data in jdata['nodelist']:
  #     pass
  #     list_data['node_id'] = convert_nodeid(list_data['node_id'])
  #   del(jdata['_id'])
  #   ana_list.append(jdata)
  #   # get_time_no = jdata["_id"]["get_time_no"]
  #   # nodelist    = jdata["nodelist"]
  #test = "aaaaa"
  #test = 0
  #for x in range(1,10):
  #  test += x

  return render_to_response('pfv/make_pfvinfo.html',  # 使用するテンプレート
                              {"time":time, "kyori":kyori}
                            )