# -*- coding: utf-8 -*-

from time import time
st = time()

# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from analyze_sta import analyze_mod
from convert_datetime import dt_from_14digits_to_iso

from pymongo import *
client = MongoClient()
db = client.nm4bd

def statistics_all(st_dt, ed_dt):
	# 時刻をiso形式に変換
	st_dt = dt_from_14digits_to_iso(st_dt)
	ed_dt = dt_from_14digits_to_iso(ed_dt)

	### DB初期化 ##############
    db.pastdata.drop()
    db.pfvinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.pfvmacinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.stayinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.staymacinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})

	analyze_mod(st_dt,ed_dt)

if __name__ == '__main__':
	statistics_all(201709041700, 201709041730)
	print(time() - st)
