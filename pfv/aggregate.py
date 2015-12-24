# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test, pcwltime, tmpcol
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

  aggregate_mod(request, startdt_int14, enddt_int14, all_bool)
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
  startdt_int14 = 20151203123700
  enddt_int14   = 20991231235959
  all_bool      = True

  aggregate_mod(request, startdt_int14, enddt_int14, all_bool)
  get_start_end_mod(request)
  ed = time.time()
  print(ed - st)


  return render_to_response('pfv/aggregate_data.html',  # 使用するテンプレート
                              {} 
                            )



def aggregate_mod(request, startdt_int14, enddt_int14, all_bool):
  ### testコレクションにstr型のget_time_noが入ってしまった場合にコメントアウト ###
  # datas = db.test.find()
  # for data in datas:
  #   data["get_time_no"] = int(data["get_time_no"])
  #   data["dt_end0"]     = int(str(data["get_time_no"])[0:13] + "0")
  #   db.test.save(data)
  #################################################################

  ag = test._get_collection().aggregate([
                                          # {"$limit":1000},
                                          {"$match":
                                                  {"dt_end0":
                                                            {"$gte":startdt_int14, "$lt":enddt_int14}
                                                  }
                                          },
                                          {"$group":
                                            {"_id":
                                              {"mac":"$mac", 
                                               "get_time_no":"$dt_end0",
                                              },
                                             "nodelist":{"$push":{"dbm":"$dbm", "node_id":"$node_id"}},
                                            },
                                          },
                                          {"$out": "tmpcol"},
                                        ],
                                      allowDiskUse=True,
                                      )

  # pcwltimeコレクション作成
  from datetime import datetime
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

  for jdata in jdatas:
    jdata['datetime'] = datetime.strptime(str(jdata['_id']['get_time_no']), '%Y%m%d%H%M%S')
    del(jdata['_id'])
    if tmp_time == 0:
      tmp_time = jdata['datetime']
    else:
      j_tmp_time = tmp_time - jdata['datetime']
      j_time = j_tmp_time.total_seconds()
      if round(j_time / 10) == 0:
        tmp_time = jdata['datetime']
      else:
        timedata = pcwltime(
                            datetime = tmp_time,
                           )
        timedata.save()
        tmp_time = jdata['datetime']

  timedata = pcwltime(
                      datetime = tmp_time,
                     )
  timedata.save()
