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

def make_pcwltime():
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
    # jdatas = db.tmppcwltime.find()
    # pcwltime.objects.all().delete()

    # for jdata in jdatas:
    # 	jdata['datetime'] = datetime.strptime(str(jdata['_id']['get_time_no']), '%Y%m%d%H%M%S')
    # 	del(jdata['_id'])
    # 	timedata = pcwltime(
    # 		datetime = jdata['datetime'],
    # 		)
    # 	timedata.save()
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


    # ag = test._get_collection().aggregate([{"$match":{"node_id":1242}}])
    # ag2 = test._get_collection().aggregate([{"$group":{"_id":{"get_time_no":"$get_time_no"}, "count":{"$sum":1}}}])
    # t = test.objects(node_id=1244).limit(25000)
    # t = test.objects(get_time_no__gte=20150603114000).limit(1000)