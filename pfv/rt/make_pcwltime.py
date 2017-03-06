# -*- coding: utf-8 -*-
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd

def make_pcwltime(iso_date):
    """
    処理済みの時刻をpcwltimeコレクションに追加
    @param  iso_date : datetime
    """
    ins_data = {"datetime":iso_date}
    db.pcwltime.insert(ins_data)