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

class test(Document):
    id          = StringField(max_length=255)
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
