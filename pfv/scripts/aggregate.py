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


startdt_int14 = 20151203123500
enddt_int14   = 20991231235959

def realtime(startdt_int14=startdt_int14, enddt_int14=enddt_int14, DEBUG=True):
    import time
    st = time.time()
    print("RealTime process")
    # startdt_int14 = 20150603000000
    # startdt_int14 = 20151203123500
    # enddt_int14   = 20991231235959
    all_bool      = DEBUG

    aggregate_mod(startdt_int14, enddt_int14, all_bool, True, False)
    if DEBUG:
        db.pastdata.remove()
        print("pastdata removed!")

    get_start_end_mod(False,False)
    ed = time.time()
    print(ed - st)

def RTtracking(startdt_int14=startdt_int14, enddt_int14=enddt_int14, DEBUG=True):
    import time
    st = time.time()
    print("RTtracking process")
    # startdt_int14 = 20150603000000
    # startdt_int14 = 20151203123500
    # enddt_int14   = 20991231235959
    all_bool      = DEBUG

    aggregate_mod(startdt_int14, enddt_int14, all_bool, True, True)
    if DEBUG:
        db.pastdata.remove()

    get_start_end_mod(False,True)
    ed = time.time()
    print(ed - st)


# dt05
min_interval = 10

def aggregate_mod(startdt_int14, enddt_int14, all_bool, RT_flag, tr_flag):
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
        cond = {"$match": {"dt_end05": {"$gte":startdt_int14, "$lt":enddt_int14} } }
        dt_end = "$dt_end05"
        min_interval = 5
    
    ag = db.trtmp.aggregate([
                            # {"$limit":1000},
                                cond,
                                {"$group":
                                    {"_id":
                                        {"mac":"$mac", 
                                        # dt05
                                         "get_time_no":dt_end,
                                         # "get_time_no":"$dt_end05",
                                        },
                                        # node_id -> ip
                                     "nodelist":{"$push":{"dbm":"$dbm", "ip":"$ip"}},
                                     # "nodelist":{"$push":{"dbm":"$dbm", "node_id":"$node_id"}},
                                    },
                                },
                                {"$out": "tmpcol"},
                            ],
                            allowDiskUse=True,
                            )

    make_pcwltime(min_interval, all_bool)
    # print("tmpcol_count:"+str(db.tmpcol.count()))
