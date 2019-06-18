# -*- coding: utf-8 -*-
from save_pfvinfo import *
from convert_ip import convert_ip
from convert_nodeid import convert_nodeid
from convert_datetime import shift_seconds
from classify import classify
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale
from datetime import datetime, timedelta

client = MongoClient()
db = client.nm4bd
db.tmpcol.create_index([("_id.get_time_no", ASCENDING), ("_id.mac", ASCENDING)])

# CONST
MIN_NODE_NUM = 1
MAX_NODE_NUM = 27
FLOOR_LIST   = ["W2-6F","W2-7F","W2-8F","W2-9F","kaiyo"]
int_time_range = 30
time_range = timedelta(seconds=int_time_range) # 過去の参照時間幅設定
TH_RSSI    = -80
repeat_cnt = 99
INT_KEEP_ALIVE = 15
KEEP_ALIVE = timedelta(seconds=INT_KEEP_ALIVE)
# 分岐点で止める機能
INTERSECTION_FUNCTION = True
# 分岐点で止めたあとに5sec stayさせる機能(上がTrueのときのみ利用可)
STAY_AFTER_INTERSECTION = False
min_interval = 5

# use Machine-Learning
USE_ML = True

def get_start_end_mod(all_st_time):
    """
    開始・終了の時刻・地点を決定するモジュール
    @param  all_st_time : datetime 開始時刻
    """
 