# -*- coding: utf-8 -*-

## 使い方　##
# 0. csv_examine_routeの指定事項（db.csvtestのインポート、解析対象クエリ指定）を確認
# 1. debug_all db.trtmpにインポートするjsonファイルのパス　（解析開始時刻）　（解析終了時刻）　を実行

from time import time
st = time()

# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from init_db import init_db
from analyze import analyze_mod
from convert_datetime import dt_from_14digits_to_iso
from csv_examine_route import csv_examine_route, make_exp_id

from pymongo import *
client = MongoClient()
db = client.nm4bd

def debug_all(json_file, st_dt, ed_dt, query_list):
	os.system("mongoimport -d nm4bd -c trtmp " + json_file)
	# db.trtmp.create_index([("get_time_no", ASCENDING),("mac", ASCENDING)])
	# db.trtmp.create_index([("get_time_no", ASCENDING)])
	# db.trtmp.create_index([("mac", ASCENDING)])
	st_dt = dt_from_14digits_to_iso(st_dt)
	ed_dt = dt_from_14digits_to_iso(ed_dt)
	analyze_mod(st_dt,ed_dt)
	csv_examine_route(query_list)

if __name__ == '__main__':
	init_db()
	# query_list = make_exp_id("161213_", 79, 88)
	# debug_all("C:/Users/Ryuta/Desktop/backup_data/rttmp/rttmp_20161214_flow.json", 201612131826, 201612131835, query_list)
	# query_list = make_exp_id("161221_", 5, 8)
	# debug_all("C:/Users/Ryuta/Desktop/backup_data/rttmp/rttmp_20161222.json", 201612211838, 201612211841, query_list)
	# query_list = make_exp_id("170127_", 1, 75)
	# debug_all("C:/Users/Ryuta/Desktop/backup_data/rttmp/rttmp_20170128_ext.json", 201701271746, 201701271835, query_list)
	query_list = make_exp_id("170128_", 1, 3)
	debug_all("C:/Users/Ryuta/Desktop/backup_data/rttmp/rttmp_20170129.json", 201701281814, 201701281815, query_list)

	
	# output = "C:/Users/Ryuta/exp_result_FF_F.csv"
	output = "C:/Users/Ryuta/exp_result170128_TT_T.csv"
	# output = "C:/Users/Ryuta/exp_result170128_TF_T.csv"
	command = 'mongoexport --sort {"exp_id":1} -d nm4bd -c examine_summary -o '+output+' --csv --fieldFile C:/Users/Ryuta/exp_result.txt'
	os.system(command)
	print(time() - st)
	