# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test, pcwltime
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd

def aggregate_data(request):
  ### testコレクションにstr型のget_time_noが入ってしまった場合にコメントアウト ###
  # datas = db.test.find()
  # for data in datas:
  #   data["get_time_no"] = int(data["get_time_no"])
  #   db.test.save(data)
  #################################################################

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
                                      )

  # pcwltimeコレクション作成
  from datetime import datetime
  ag = test._get_collection().aggregate([
                                        {"$group":
                                          {"_id":
                                            {"get_time_no":"$get_time_no",}
                                          },
                                        },
                                        {"$out": "tmppcwltime"},
                                      ],
                                    allowDiskUse=True,
                                    )

  jdatas = db.tmppcwltime.find().sort("_id")
  pcwltime.objects.all().delete()
  tmp_time = 0 #一つ前の時刻
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

  return render_to_response('pfv/aggregate_data.html',  # 使用するテンプレート
                              {} 
                            )