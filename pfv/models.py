# -*- coding: utf-8 -*-
from django.db import models
from mongoengine import *

#データリスト用
class pr_req(Document):
    _id         = StringField(max_length=255)
    node_id     = IntField()
    get_time_no = IntField()
    mac         = StringField(max_length=255)
    rssi        = IntField()
    dbm         = IntField()
    sequence    = IntField()
    timestamp   = IntField()

    meta = {
        "db_alias" : "nm4bd",
    }

# PCWLのノード情報
class pcwlnode(Document):
    pcwl_id = IntField()
    pos_x = IntField()
    pos_y = IntField()
    next_id = ListField(IntField())
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "pcwl_id" : 2,
    # "pos_x" : 990,
    # "pos_y" : 130,
    # "next_id" : [ 1, 3 ]
    # "floor" : "W2-6F",

# 人流情報
class pfvinfo(Document):
    plist = ListField(DictField())
    datetime = DateTimeField()
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "datetime" : ISODate("2015-06-03T13:04:06Z"),
    # "floor" : "W2-6F",
    # "plist" : [ { "direction" : [ 1, 2 ], "size" : 0 }, { "direction" : [ 2, 1 ], "size" : 0 },...]

# 人流情報(6F実験用)
class pfvinfoexperiment(Document):
    plist = ListField(DictField())
    datetime = DateTimeField()
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

class pfvinfoexperiment2(Document):
    plist = ListField(DictField())
    datetime = DateTimeField()
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

# 人流情報(mac情報付き)
class pfvmacinfo(Document):
    datetime = DateTimeField()
    mac = StringField()
    route = ListField(ListField(IntField))
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "datetime" : ISODate("2015-06-03T13:04:06Z"),
    # "floor" : "W2-6F",
    # "mac" : "00:24:d6:43:e7:dc",
    # "plist" : [ { "direction" : [ 1, 2 ], "size" : 0 }, { "direction" : [ 2, 1 ], "size" : 0 },...]
    # "route" : [[1,2],[2,3],[3,4]]

# 滞留端末情報
class stayinfo(Document):
    plist = ListField(DictField())
    datetime = DateTimeField()
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "datetime" : ISODate("2015-09-25T18:11:37Z"),
    # "floor" : "W2-6F",
    # "plist" : [ { "pcwl_id" : 1, "size" : 0 }, { "pcwl_id" : 2, "size" : 1 },...]

# 滞留端末情報(mac情報付き)
class staymacinfo(Document):
    pcwl_id = IntField()
    mac = StringField()
    datetime = DateTimeField()
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "datetime" : ISODate("2015-09-25T18:11:37Z"),
    # "floor" : "W2-6F",
    # "mac" : "54:9f:13:10:a3:b4"
    # "plist" : [ { "pcwl_id" : 1, "size" : 0 }, { "pcwl_id" : 2, "size" : 1 },...]

# ブックマーク情報
class bookmark(Document):
    name = StringField(max_length=255)
    url = StringField(max_length=255)
    frequency = IntField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "name" : "6月3日人流データ",
    # "url" : "?datetime=20150603122120&timerange=60&experiment=0&language=jp",
    # "frequency" : 0

# RealTimeビュー用生データ(Real Time RAW data)
class rtraw(Document):
    node_id     = IntField()
    get_time_no = IntField()
    mac         = StringField(max_length=255)
    rssi        = IntField()
    dbm        = IntField()

    meta = {
        "db_alias" : "nm4bd",
    }

class test(Document):
    _id          = StringField(max_length=255)
    node_id     = IntField()
    get_time_no = IntField()
    mac         = StringField(max_length=255)
    rssi        = IntField()
    dbm         = IntField()
    sequence    = IntField()
    timestamp   = IntField()

    meta = {
    	"db_alias" : "nm4bd",
    }

class rttmp(Document):
    _id          = StringField(max_length=255)
    node_id     = IntField()
    get_time_no = IntField()
    mac         = StringField(max_length=255)
    rssi        = IntField()
    dbm         = IntField()
    # sequence    = IntField()
    # timestamp   = IntField()

    meta = {
        "db_alias" : "nm4bd",
    }

class tmpcol(Document):
    _id = DictField()
    # nodelist = ListField(DictField())
    # mac         = StringField(max_length=255)
    # rssi        = IntField()
    # get_time_no = IntField()
    # node_id     = IntField()
    mac         = StringField()
    get_time_no = IntField()
    nodelist    = ListField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "_id" : { "get_time_no" : NumberLong("20150603060002"), "mac" : "00:15:af:e4:e1:ac" },
    # "nodelist" : [ { "node_id" : 1237, "dbm" : -89 } ]

# RT用過去データ一時保存コレクション
class pastdata(Document):
    mac         = StringField()
    update_dt   = DateTimeField()
    nodecnt_dict= DictField() 
    pastlist    = ListField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "mac" : "xx:xx:xx:xx:xx:xx",
    # "update_dt":datetime.datetime(2015,12,3,12,35,30),
    # "nodecnt_dict":{"W2-6F":{1:0,2:0,3:0...},
    #                 "W2-7F":{1:0,2:0,3:0...}
    #                },    
    # "pastlist": [ {"dt":datetime.datetime(2015,12,3,12,35,00),
    #                "start_node":{"floor":"W2-6F", "pcwl_id":10, "rssi":-60},
    #                "node":[{"floor":"W2-6F", "pcwl_id":10, "rssi":-60},
    #                         {                                         },...
    #                        ],
    #               },
    #               {"dt":...
    #               },...
    #             ]


class pcwlroute(Document):
    query = ListField(IntField())
    dlist = ListField(ListField(DictField()))
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "query" : [ 14, 24 ],
    # "floor" : "W2-6F",
    # "dlist" : [ [ { "distance" : 60.8276253029822, "direction" : [ 14, 15 ] }, { "distance" : 68.00735254367721, "direction" : [ 15, 16 ] }, { "distance" : 75.16648189186454, "direction" : [ 16, 24 ] } ] ]

class pcwltime(Document):
    _id = StringField()
    datetime = DateTimeField()

    meta = {
        "db_alias" : "nm4bd",
    }

    # サンプル
    # "datetime" : ISODate("2015-06-03T14:23:39Z")

# heatmapの色づけ情報
class heatmapinfo(Document):
    datetime = DateTimeField()
    coordinate_size = ListField(DictField())
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }
