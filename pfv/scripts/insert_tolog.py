# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

import sys
import json
from pymongo import *
from mongoengine import *
from convert_datetime import *
# from pfv.models import timeoutlog, pcwliplist, tmptolog, hourlytolog


# mongoDBに接続
client = MongoClient()
db = client.nm4bd

##### hourlyto(timeout)log 作成手順 #####
# usage: python insert_tolog json_file_name str_st(14 digits) str_ed
# 1. execute this script with the usage
# 2. in the directory containing "fields.txt", execute the following command w/ cmd
#    mongoexport --sort {"datetime":1} -d nm4bd -c hourlytolog -o hourlytolog.csv --csv --fieldFile fields.txt

# (how to make "fields.txt")
#   0.execute this script with the usage
# 	1.key一覧取得
#   	mongo nm4bd --quiet --eval "for (key in db.hourlytolog.findOne()) print(key)" > fields.txt
# 	2.フィールド一覧ソート
#   	python txt_sort.py fields.txt
# 	3.不要なフィールド(_id等)削除 & datetime先頭に移動

def insert_tolog(file,st,ed):
	f = open(file, 'r')
	# f = json.dumps(f)
	# datas = json.load(f)
	# f.close()
	for line in f:
		line = json.loads(line)
		del(line["_id"])
		print(line)
		db.tolog_test.insert(line)
	
	db.hourlytolog.remove({})
	iso_st = dt_from_14digits_to_iso(st)
	iso_ed = dt_from_14digits_to_iso(ed)
	print(iso_st)
	print(iso_ed)
	gte = iso_st
	lt  = shift_hours(gte, 1)
	ip_list = []
	ip_list += db.pcwliplist.find()
	for ip_data in ip_list:
		# ip_data: whose elements are "floor", "pcwl_id", "ip"
		ip_data["log_key"] = str(ip_data["floor"]) + "-" + str(ip_data["pcwl_id"])

	while (lt <= iso_ed):
		print(gte)
		hourly_data = {}
		hourly_data["datetime"] = gte
		for ip_data in ip_list:
	  		ip = str(ip_data["ip"])
	  		count_sum = db.timeoutlog.find({"datetime":{"$gte":gte,"$lt":lt},"timeout_ip":ip}).count()
	  		hourly_data[ip_data["log_key"]] = count_sum
	  	
		db.hourlytolog.insert(hourly_data)
		gte = shift_hours(gte,1)
		lt  = shift_hours(gte,1)

	# db.timeoutlog.remove({})

if len(sys.argv) < 4:
	print ("usage: python insert_tolog json_file_name str_st(14 digits) str_ed")
	exit()

json_file = sys.argv[1] #　jsonファイルのパス
str_st = sys.argv[2] # 14桁のstr、例："20160929000000"
str_ed = sys.argv[3]
insert_tolog(json_file,str_st,str_ed)
