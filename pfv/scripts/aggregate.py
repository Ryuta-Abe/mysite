# -*- coding: utf-8 -*-
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

def aggregate_mod(startdt_iso, enddt_iso):
    # cond = {"$limit":1000000}
    cond = {"$match": {"dt_end05": {"$gte":startdt_iso, "$lt":enddt_iso} } }
    # cond = {"$match": {"dt_end05": {"$gte":startdt_iso, "$lt":enddt_iso},"mac":"00:11:81:10:01:17" } } # tag
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