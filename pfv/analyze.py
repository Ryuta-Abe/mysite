# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test, tmpcol
from pfv.convert_nodeid import *
from pfv.get_start_end import name_filter
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd

def analyze_direction(request):
  from datetime import datetime

  ag = db.tmpcol.find().sort("_id.mac").sort("_id.get_time_no",-1).limit(100)
  ana_list = []
  for jdata in ag:
    jdata['id'] = jdata['_id']
    jdata['id']['get_time_no'] = datetime.strptime(str(jdata['id']['get_time_no']), '%Y%m%d%H%M%S')
    jdata['nodelist'] = sorted(jdata['nodelist'], key=lambda x:x["dbm"], reverse=True)
    for list_data in jdata['nodelist']:
      list_data['floor']   = convert_nodeid(list_data['node_id'])['floor']
      list_data['node_id'] = convert_nodeid(list_data['node_id'])['node_id']

    del(jdata['_id'])
    jdata["id"]["mac"] = name_filter(jdata["id"]["mac"])
    ana_list.append(jdata)
  return render_to_response('pfv/analyze_direction.html',  # 使用するテンプレート
                              {'ag': ana_list} 
                            )