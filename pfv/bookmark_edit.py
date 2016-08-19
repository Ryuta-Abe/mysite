# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import bookmark
from pfv.views import render_json_response
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd
# db.tmpcol.create_index([("get_time_no", DESCENDING), ("mac", ASCENDING)])

def bookmark_edit(request):

  # urlからクエリの取り出し
  add = int(request.GET.get('add', 0))
  name = request.GET.get('name', 'bookmark_name')
  date_time = request.GET.get('datetime', '20150603122130')
  timerange = int(request.GET.get('timerange', 10))
  language = request.GET.get('language', 'jp')
  mac = request.GET.get('mac', '')
  floor = request.GET.get('floor', 'W2-6F')
  delete = int(request.GET.get('delete', 0))

  # ブックマーク追加
  if add == 1:
    url = "?datetime="+date_time+"&timerange="+str(timerange)+"&language="+language+"&mac="+mac+"&floor="+floor
    db.bookmark.insert({'url':url,'name':name,'frequency':0})
    return render_json_response(request,{'url':url,'name':name,'frequency':0})

  # ブックマーク削除
  elif delete == 1:
    db.bookmark.remove({"name":name})
    return render_json_response(request,{'response':'Bookmarks deleted'})

  # ブックマーク全削除
  elif delete == 2:
    db.bookmark.remove()
    return render_json_response(request,{'response':'Bookmarks deleted'})

  #tagtrack用のbookmark関連
  elif add == 2:
    url = "?datetime="+date_time+"&timerange="+str(timerange)+"&language="+language+"&mac="+mac+"&floor="+floor
    db.bookmark.insert({'url':date_time,'name':name,'frequency':0})
    return render_json_response(request,{'url':date_time,'name':name,'frequency':0})