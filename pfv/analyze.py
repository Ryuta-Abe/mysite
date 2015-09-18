# -*- coding: utf-8 -*-
# from django.http import HttpResponse
# from django.shortcuts import render_to_response, get_object_or_404, redirect
# from django.template import RequestContext

# from models import pr_req, test, pcwlnode
from convert_nodeid import *
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

# 今日の日付
d = datetime.datetime.today() # 2014-11-20 19:41:51.011593
d = str(d.year)+("0"+str(d.month))[-2:]+("0"+str(d.day))[-2:]+("0"+str(d.hour))[-2:]+("0"+str(int(d.minute/5)*5))[-2:] # 201411201940
lt = datetime.datetime.today()

def __init__(self):
  ag = test._get_collection().aggregate([{"$group":{"_id":{"mac":"$mac", "get_time_no":"$get_time_no"}, "count":{"$sum":1}}}])
  print (ag)