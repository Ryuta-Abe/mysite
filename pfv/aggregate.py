# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test, pcwltime, tmpcol, pastdata, rttmp
from pfv.get_start_end import get_start_end, get_start_end_mod
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd

# aggredateのみ
def aggregate_data(request):
  import time
  st = time.time()
  print("aggregate all")
  # startdt_int14 = 20150603000000
  startdt_int14 = 20151203123600
  enddt_int14   = 20991231235959
  all_bool      = True

  aggregate_mod(startdt_int14, enddt_int14, all_bool, False)
  ed = time.time()
  print(ed - st)

  return render_to_response('pfv/aggregate_data.html',  # 使用するテンプレート
                              {} 
                            )

# aggregate -> get_start_end -> saveまで通しで
def process_all(request):
  import time
  st = time.time()
  print("aggregate partly")
  # startdt_int14 = 20150603000000
  startdt_int14 = 20151203123500
  enddt_int14   = 20991231235959
  all_bool      = True

  aggregate_mod(startdt_int14, enddt_int14, all_bool, False)
  db.pastdata.remove()
  get_start_end_mod(False)
  ed = time.time()
  print(ed - st)

  return render_to_response('pfv/aggregate_data.html',  # 使用するテンプレート
                              {} 
                            )

startdt_int14 = 20151203123500
enddt_int14   = 20991231235959

def realtime(startdt_int14=startdt_int14, enddt_int14=enddt_int14, DEBUG=True):
  import time
  st = time.time()
  print("RealTime process")
  # startdt_int14 = 20150603000000
  # startdt_int14 = 20151203123500
  # enddt_int14   = 20991231235959
  all_bool      = DEBUG

  aggregate_mod(startdt_int14, enddt_int14, all_bool, True)
  if DEBUG == True:
    db.pastdata.remove()

  get_start_end_mod(False)
  ed = time.time()
  print(ed - st)

def aggregate_mod(startdt_int14, enddt_int14, all_bool, RT_flag):
  ### testコレクションにstr型のget_time_noが入ってしまった場合にコメントアウト ###
  # datas = db.test.find()
  # for data in datas:
  #   data["get_time_no"] = int(data["get_time_no"])
  #   data["dt_end0"]     = int(str(data["get_time_no"])[0:13] + "0")
  #   db.test.save(data)
  #################################################################
  if RT_flag:
    col_name = rttmp
    cond = {"$limit":1000000}
    # print("rttmp_count:"+str(db.col_name.count()))
  else:
    col_name = test
    cond = {"$match": {"dt_end0": {"$gte":startdt_int14, "$lt":enddt_int14} } }

  ag = col_name._get_collection().aggregate([
                                          # {"$limit":1000},
                                            cond,
                                            {"$group":
                                              {"_id":
                                                {"mac":"$mac", 
                                                # dt05
                                                 "get_time_no":"$dt_end0",
                                                },
                                               "nodelist":{"$push":{"dbm":"$dbm", "node_id":"$node_id"}},
                                              },
                                            },
                                            {"$out": "tmpcol"},
                                          ],
                                        allowDiskUse=True,
                                        )
  db.rttmp.remove()
  print("tmpcol_count:"+str(db.tmpcol.count()))
  # pcwltimeコレクション作成
  from datetime import datetime, timedelta
  ag = tmpcol._get_collection().aggregate([
                                            {"$group":
                                              {"_id":
                                                {"get_time_no":"$_id.get_time_no",}
                                              },
                                            },
                                            {"$out": "tmppcwltime"},
                                          ],
                                        allowDiskUse=True,
                                        )
  if all_bool: # 全件ならTrueでpcwltimeをリセット
    pcwltime.objects.all().delete()

  tmp_time = 0 #一つ前の時刻
  jdatas = db.tmppcwltime.find().sort("_id")

  # dt05
  for jdata in jdatas:
    jdata['datetime'] = datetime.strptime(str(jdata['_id']['get_time_no']), '%Y%m%d%H%M%S')
    del(jdata['_id'])
    count = db.pcwltime.find({"datetime":jdata['datetime']}).count()
    if (count == 0):
      pasttime = db.pcwltime.find().sort("datetime",-1).limit(1)
      if (pasttime.count() != 0):
        pasttime = pasttime[0]
        while (10 < (jdata['datetime'] - pasttime["datetime"]).seconds <= 60):
          # dt05
          pasttime["datetime"] = pasttime["datetime"] + timedelta(seconds = 10)
          timedata = pcwltime(
                              datetime = pasttime['datetime'],
                             )
          timedata.save()

      timedata = pcwltime(
                          datetime = jdata['datetime'],
                         )
      timedata.save()

