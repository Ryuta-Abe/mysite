# -*- coding: utf-8 -*-
from get_start_end import get_start_end_mod
from convert_nodeid import *
from make_pcwltime import *

from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd

# dt05
min_interval = 10

def aggregate_mod(startdt_iso, enddt_iso, all_bool, RT_flag, tr_flag):
    if RT_flag:
        cond = {"$limit":1000000}
        if tr_flag:
            col_name = trtmp
            dt_end   = "$dt_end05"
            min_interval = 5
        else:
            col_name = rttmp
            dt_end   = "$dt_end05"
    else:
        cond = {"$match": {"dt_end05": {"$gte":startdt_iso, "$lt":enddt_iso} } }
        dt_end = "$dt_end05"
        min_interval = 5
    
    ag = db.trtmp.aggregate([
                                cond,
                                {"$group":
                                    {"_id":
                                        {"mac":"$mac", 
                                         "get_time_no":dt_end,
                                        },
                                     "nodelist":{"$push":{"dbm":"$dbm", "ip":"$ip"}},
                                    },
                                },
                                {"$out": "tmpcol"},
                            ],
                            allowDiskUse=True,
                            )

    make_pcwltime_test(startdt_iso)