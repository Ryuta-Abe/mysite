# -*- coding: utf-8 -*-
from convert_nodeid import *
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd

def aggregate_mod(startdt_iso, enddt_iso):
    """
    PRデータ集計モジュール
    "5秒毎"のPRデータを集計することを想定
    @param  startdt_iso : datetime
    @param  enddt_iso   : datetime
    """
    cond = {"$match": {"get_time_no": {"$gte":startdt_iso, "$lt":enddt_iso} } }
    ag = db.trtmp.aggregate([
                                cond,
                                {"$group":
                                    {"_id":
                                        {"mac":"$mac", 
                                         "get_time_no":"$get_time_no",
                                        },
                                     "nodelist":{"$push":{"dbm":"$dbm", "ip":"$ip"}},
                                    },
                                },
                                {"$out": "tmpcol"},
                            ],
                            allowDiskUse=True,
                            )

    make_pcwltime(startdt_iso)


def make_pcwltime(iso_date):
    """
    処理済みの時刻をpcwltimeコレクションに追加
    @param  iso_date : datetime
    """
    ins_data = {"datetime":iso_date}
    db.pcwltime.insert(ins_data)