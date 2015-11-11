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

# 人流情報
class pfvinfo(Document):
    plist = ListField(DictField())
    datetime = DateTimeField()
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

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
    direction = ListField(ListField(IntField()))
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

# 滞留端末情報
class stayinfo(Document):
    plist = ListField(DictField())
    datetime = DateTimeField()
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

# ブックマーク情報
class bookmark(Document):
    name = StringField(max_length=255)
    url = StringField(max_length=255)
    frequency = IntField()

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

class pcwlroute(Document):
    query = ListField(IntField())
    dlist = ListField(ListField(DictField()))
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

class pcwltime(Document):
    _id = StringField()
    datetime = DateTimeField()

    meta = {
        "db_alias" : "nm4bd",
    }