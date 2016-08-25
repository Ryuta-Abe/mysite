# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from pfv.aggregate import *
from pfv.models import raw100
from pfv.convert_datetime import dt_from_14digits_to_iso, shift_seconds

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
    # 入力は14桁数字(int)
    lt = str(args[0])
    dt_end = int(str(lt)[-1:])
    if (0 <= dt_end <=4):
      lt = int(str(lt)[0:13] + "0")
    elif (5 <= dt_end <=9):
      lt = int(str(lt)[0:13] + "5")

    lt  = dt_from_14digits_to_iso(str(lt))
    gte = shift_seconds(lt, -5)

    cond = {"on_recv":{"$gte"gte, "$lt":lt}}

    datas = db.raw100.find(cond)

    col_name = raw100
    # TODO
    # ag = col_name._get_collection().aggregate([
    #                                     # {"$limit":1000},
    #                                       cond,
    #                                       {"$group":
    #                                         {"_id":
    #                                           {"mac":"$mac", 
    #                                           # dt05
    #                                            "get_time_no":dt_end,
    #                                            # "get_time_no":"$dt_end05",
    #                                           },
    #                                          "nodelist":{"$push":{"dbm":"$dbm", "node_id":"$node_id"}},
    #                                         },
    #                                       },
    #                                       {"$out": "raw100tmp"},
    #                                     ],
    #                                   allowDiskUse=True,
    #                                   )


    # startdt, enddt = int(args[0]),int(args[1])
    # print(startdt, enddt)

    # realtime(startdt,enddt,False)
    # RTtracking(startdt,enddt,False)

    # db.rttmp.remove()
    # db.trtmp.remove()

    print(time.time() - st)
