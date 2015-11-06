# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd

def aggregate_data(request):
  datas = db.test.find()
  for data in datas:
    data["get_time_no"] = int(data["get_time_no"])
    db.test.save(data)

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

  return render_to_response('pfv/aggregate_data.html',  # 使用するテンプレート
                              {} 
                            )