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
from pymongo import *
client = MongoClient()
db = client.nm4bd
from init_db import init_db
from init_all import init_all
from analyze import analyze_mod
from convert_datetime import dt_from_14digits_to_iso
from csv_examine_route import csv_examine_route, make_exp_id
from make_pcwlnode import make_half_pcwlnode, make_pcwlnode
import config
from configparser import ConfigParser
### TODO:以下を変更 ###
### config.pyの各種パラメーターを変更  ###
import_flag = True  # trtmp, csvtestにインポートしなおすかどうか
date = "20190413"
st_dt = date + "2149"
ed_dt = date + "2334" ## 解析終了時刻 """
st_exp_id = 1  # 開始クエリ番号
ed_exp_id = 96 # 終了クエリ番号
###
# INI_FILE = "../config.ini"
# ini = config.read_config_file(INI_FILE)
# DELETES_FP = ini.getboolean("AP_FP", "DELETES_FP")

def debug_all(st_dt, ed_dt, query_list):
	DELETES_FP = config.DELETES_FP
	# ini = config.read_config_file(INI_FILE)
	# DELETES_FP = ini.getboolean("AP_FP", "DELETES_FP")
	# print(DELETES_FP)
	if DELETES_FP:
		make_half_pcwlnode()
	db.trtmp.create_index([("get_time_no", ASCENDING),("mac", ASCENDING)])
	# db.trtmp.create_index([("get_time_no", ASCENDING)])
	db.trtmp.create_index([("mac", ASCENDING)])
	st_dt = dt_from_14digits_to_iso(st_dt)
	ed_dt = dt_from_14digits_to_iso(ed_dt)
	analyze_mod(st_dt,ed_dt)
	csv_examine_route(query_list)  ## TODO: examine_route系の変更

if __name__ == '__main__':
	# init_db()
	init_all()
	path = "../../working/"

	short_date = date[2:]
	query_list = make_exp_id(short_date + '_', st_exp_id, ed_exp_id)  

	json_file_name = "rttmp3_" + date + ".json" 
	json_file = path + json_file_name
	param_file_name = "exp_param_" + date + ".csv" 
	param_file = path + param_file_name

	if import_flag:
		os.system("mongoimport -d nm4bd -c trtmp " + json_file + " --drop")
		os.system("mongoimport -d nm4bd -c csvtest --headerline --columnsHaveTypes --type=csv " + param_file + " --drop")
	
	# 準備終了、デバック開始
	debug_all(st_dt,ed_dt,query_list)

	# 結果を出力
	output_file_name = date + ".csv"
	output_file = path + output_file_name

	command = 'mongoexport --sort {"exp_id":1} -d nm4bd -c examine_summary -o '+output_file+' --type=csv --fieldFile ../../mlfile/txt/exp_result.txt'
	os.system(command)
	