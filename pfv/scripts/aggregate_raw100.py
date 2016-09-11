# -*- coding: utf-8 -*-
from convert_datetime import *

import datetime
from datetime import datetime, timedelta
import time

from pymongo import *
client = MongoClient()
db = client.nm4bd

lt = "20160821160000"
gte = "20160821180000"

def aggregate_raw100(lt=lt):
    st = time.time()
    # 入力は14桁数字(int)
    lt = str(dt_end_to_05(lt))
    lt  = dt_from_14digits_to_iso(lt)

    gte = shift_seconds(lt, -5)

    cond = {"$match": {"on_recv": {"$gte":gte, "$lt":lt} } }
    ag = db.raw100.aggregate([
                              cond,
                              {"$group":
                                {"_id":
                                        {
                                           "mac":"$mac", 
                                           "get_time_no":"$on_recv",
                                           "ap_ip":"$ap_ip"
                                        },
                                 "dbm":{
                                        "$max":"$dbm"
                                        },
                                },
                              },
                              {"$group":
                                {"_id":
                                        {
                                           "mac":"$_id.mac", 
                                           "get_time_no":"$_id.get_time_no",
                                        },
                                 "nodelist":{
                                            "$push":
                                                {
                                                "ap_ip":"$_id.ap_ip",
                                                "dbm":"$dbm"
                                                },
                                            }
                                },
                              },
                              {"$out": "raw100tmp"},
                            ],
                          allowDiskUse=True,
                          )

    print(time.time() - st)

aggregate_raw100()