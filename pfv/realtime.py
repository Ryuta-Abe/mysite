# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import rtraw
from pfv.views import render_json_response
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd

def rt_raw_save(request):

  # urlからクエリの取り出し
  add = int(request.GET.get('add', 0))
  delete = int(request.GET.get('delete', 0))
  node_id = int(request.GET.get('node_id', 1))
  mac = request.GET.get('mac', '')
  get_time_no = int(request.GET.get('get_time_no', 20151203123456))
  rssi = int(request.GET.get('rssi', 30))
  dbm = int(request.GET.get('dbm', -50))

  # Real Time RAW data 追加(例:http://localhost:8000/pfv/rt_raw_save/?add=1&node_id=1&mac=aa:aa:aa:aa:aa:aa&get_time_no=20151203123456&rssi=50&dbm=-80)
  if add == 1:
    db.rtraw.insert({'node_id':node_id,'mac':mac,'get_time_no':get_time_no,'rssi':rssi,'dbm':dbm})
    return render_json_response(request,{'node_id':node_id,'mac':mac,'get_time_no':get_time_no,'rssi':rssi,'dbm':dbm})

  # Real Time RAW data 削除(指定のmacのみ)
  elif delete == 1:
    db.rtraw.remove({"mac":mac})
    return render_json_response(request,{'response':'mac:'+str(mac)+' rtraw deleted'})

  # Real Time RAW data 全削除
  elif delete == 2:
    db.rtraw.remove()
    return render_json_response(request,{'response':'All rtraw deleted'})
