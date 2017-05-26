# -*- coding: utf-8 -*-

from pymongo import *
client = MongoClient()
db = client.nm4bd
db.raw100_test2.drop()

"""
raw100(8Fの生データ)集計・整形スクリプト
"""
ag = db.raw100_test.aggregate([
                            # cond,
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
                            # {"$unwind":"$nodelist"},
                            {"$out": "raw100tmp"},
                          ],
                          allowDiskUse=True,
                        )

datas = db.raw100tmp.find()
for data in datas:
  # print(data)
  ins_dict = {}
  ins_dict["get_time_no"] = data["_id"]["get_time_no"]
  ins_dict["mac"] = data["_id"]["mac"]
  # print(data["_id"]["get_time_no"], data["_id"]["mac"])
  for pr_data in data["nodelist"]:
    # print(pr_data["ip"],pr_data["dbm"])
    ins_dict["ip"] = pr_data["ip"]
    ins_dict["dbm"] = pr_data["dbm"]
    if "_id" in ins_dict:
      del(ins_dict["_id"])
    # print("insert:"+str(ins_dict))
    db.raw100_test2.insert(ins_dict)



