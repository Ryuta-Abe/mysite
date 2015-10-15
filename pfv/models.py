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

    meta = {
        "db_alias" : "nm4bd",
    }

# 人流情報
class pfvinfo(Document):
    plist = ListField(DictField())
    datetime = DateTimeField()

    meta = {
        "db_alias" : "nm4bd",
    }

# 滞留端末情報
class stayinfo(Document):
    plist = ListField(DictField())
    datetime = DateTimeField()

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
    _id = StringField()
    # nodelist = ListField(DictField())
    # mac         = StringField(max_length=255)
    # rssi        = IntField()
    # get_time_no = IntField()
    # node_id     = IntField()
    mac         = ListField()
    get_time_no = ListField()
    nodelist    = ListField()

    meta = {
        "db_alias" : "nm4bd",
    }

class pcwlroute(Document):
    query = ListField(IntField())
    dlist = ListField(ListField(DictField()))

    meta = {
        "db_alias" : "nm4bd",
    }

class pcwltime(Document):
    _id = StringField()
    datetime = DateTimeField()

    meta = {
        "db_alias" : "nm4bd",
    }