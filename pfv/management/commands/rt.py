# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from pfv.models import rttmp,trtmp

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
    # dt0
    datas = db.rttmp.find()
    for data in datas:
      data["get_time_no"] = int(data["get_time_no"])
      data["dt_end0"] = int(str(data["get_time_no"])[0:13] + "0")
      db.rttmp.save(data)

    # dt05
    datas = db.trtmp.find()
    for data in datas:
      dt_end = int(str(data["get_time_no"])[-1:])
      if (0 <= dt_end <=4):
        data["dt_end05"] = int(str(data["get_time_no"])[0:13] + "0")
      elif (5 <= dt_end <=9):
        data["dt_end05"] = int(str(data["get_time_no"])[0:13] + "5")
      db.trtmp.save(data)
    
    startdt, enddt = int(args[0]),int(args[1])
    print(startdt, enddt)

    # realtime(startdt,enddt,False)
    RTtracking(startdt,enddt,False)

    db.rttmp.remove()
    db.trtmp.remove()

    print(time.time() - st)
