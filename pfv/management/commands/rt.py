# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from pfv.aggregate import *
from pfv.models import rttmp

import json
import math
import datetime
import locale
from datetime import datetime, timedelta
import time

client = MongoClient()
db = client.nm4bd

import logging

class Command(BaseCommand):
  # args = '<target_id target_id ...>'
  help = u'RealTime process'

  def handle(self, *args, **options):
  	st = time.time()

  	datas = db.rttmp.find()
  	for data in datas:
  		data["get_time_no"] = int(data["get_time_no"])
      # dt05
  		data["dt_end0"]     = int(str(data["get_time_no"])[0:13] + "0")
  		db.rttmp.save(data)

  	startdt, enddt = int(args[0]),int(args[1])
  	print(startdt, enddt)

  	realtime(startdt,enddt,False)
  	db.rttmp.remove()
  	
  	print(time.time() - st)
