# -*- coding: utf-8 -*-
from convert_datetime import *

import datetime
from datetime import datetime, timedelta
import time

from pymongo import *
client = MongoClient()
db = client.nm4bd

lt  = "20160821160000"
gte = "20160821180000"

def aggregate_raw100(lt=lt):
  st = time.time()
  gte = shift_seconds(lt, -5)
  cond_lt  = shift_hours(lt, -9)
  cond_gte = shift_hours(gte, -9)

  # db.raw100.find().forEach(function (x) {db.raw100_backup.save(x)})
  dt_cond = {"on_recv": {"$gte":cond_gte, "$lt":cond_lt}}
  raw_datas = db.raw100.find(dt_cond)
  for data in raw_datas:
    data["on_recv"] = shift_hours(data["on_recv"], 9)
    db.raw100_backup.insert(data)
    db.raw100.save(data)

  # lt  = shift_hours(lt, 9)
  # gte = shift_hours(gte, 9)

  dt_cond = {"on_recv": {"$gte":gte, "$lt":lt}}
  cond = {"$match":dt_cond}
  ag = db.raw100.aggregate([
                            cond,
                            {"$group":
                              {"_id":
                                  {
                                     "mac":"$mac", 
                                     "get_time_no":"$on_recv",
                                     "ip":"$ap_ip"
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
                                      "ip":"$_id.ip",
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
  insert_raw100_to_tmpcol()

def insert_raw100_to_tmpcol():
  datas = db.raw100tmp.find()
  for data in datas:
    # print("------------------")
    # print(data)
    data["_id"]["get_time_no"] = iso_to_end05iso(data["_id"]["get_time_no"])
    cond = {
            "_id.mac":data["_id"]["mac"],
            "_id.get_time_no":data["_id"]["get_time_no"],
            }
    ins_col = db.tmpcol
    tmpcol_data = ins_col.find_one(cond)

    if tmpcol_data != None:
      for node in data["nodelist"]:
        tmpcol_data["nodelist"].append(node)
      ins_col.save(tmpcol_data)
    else:
      ins_col.insert(data)


# aggregate_raw100()
