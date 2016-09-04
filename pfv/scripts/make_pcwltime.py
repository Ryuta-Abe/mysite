# -*- coding: utf-8 -*-
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd

def make_pcwltime(min_interval, all_bool):
    # pcwltimeコレクション作成
    from datetime import datetime, timedelta
    ag = db.tmpcol.aggregate([
                                {"$group":
                                    {"_id":
                                        {"get_time_no":"$_id.get_time_no",}
                                    },
                                },
                                {"$out": "tmppcwltime"},
                            ],
                            allowDiskUse=True,
                            )
    if all_bool: # 全件ならTrueでpcwltimeをリセット
        db.pcwltime.remove()

    tmp_time = 0 #一つ前の時刻
    jdatas = db.tmppcwltime.find().sort("_id")

    # dt05
    for jdata in jdatas:
        jdata["datetime"] = datetime.strptime(str(jdata["_id"]["get_time_no"]), "%Y%m%d%H%M%S")
        del(jdata["_id"])
        exist = db.pcwltime.find({"datetime":jdata["datetime"]}).count()
        # 重複確認、なければ登録
        if (exist == 0):
            pasttime = db.pcwltime.find().sort("datetime",-1).limit(1)
            if (pasttime.count() != 0):
                pasttime = pasttime[0]
                while (min_interval < (jdata["datetime"] - pasttime["datetime"]).seconds <= 60):
                    # dt05
                    pasttime["datetime"] = pasttime["datetime"] + timedelta(seconds = min_interval)
                    timedata = {"datetime":pasttime["datetime"]}
                    db.pcwltime.insert(timedata)

            timedata = {"datetime" : jdata["datetime"]}
            db.pcwltime.insert(timedata)
