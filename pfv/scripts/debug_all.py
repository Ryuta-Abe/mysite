# -*- coding: utf-8 -*-

## 使い方　##
# 0. csv_examine_routeの指定事項（db.csvtestのインポート、解析対象クエリ指定）を確認
# 1. debug_all db.trtmpにインポートするjsonファイルのパス　（解析開始時刻）　（解析終了時刻）　を実行

## 実行前に指定　##
st_dt = 201612211800
ed_dt = 201612211900
#################

from time import time
st = time()
import os
import sys
from convert_datetime import dt_from_14digits_to_iso
from init_db import init_db
from analyze import analyze_mod
from csv_examine_route import csv_examine_route

from pymongo import *
client = MongoClient()
db = client.nm4bd

def debug_all(json_file,st_dt = st_dt,ed_dt = ed_dt):
	init_db()
	os.system("mongoimport -d nm4bd -c trtmp " + json_file)
	st_dt = dt_from_14digits_to_iso(st_dt)
	ed_dt = dt_from_14digits_to_iso(ed_dt)
	analyze_mod(st_dt,ed_dt)
	csv_examine_route()

if __name__ == '__main__':
	param = sys.argv
	json_file = param[1]
	if len(param) == 2:
		debug_all(json_file)
	elif len(param) == 4:
		st_dt = param[2]
		ed_dt = param[3]
		debug_all(json_file,st_dt,ed_dt)
	print(time() - st)
	