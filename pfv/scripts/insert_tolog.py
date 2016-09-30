# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from pymongo import *
from mongoengine import *
from pfv.models import timeoutlog, pcwliplist, tmptolog, hourlytolog
from pfv.scripts.convert_datetime import *

# mongoDBに接続
client = MongoClient()
db = client.nm4bd
import sys
import json


json_file = sys.argv[1]　#　jsonファイルのパス
str_st = sys.argv[2] # 14桁のstr、例："20160929000000"
str_ed = sys.argv[3]
insert_tolog(json_file,st,ed)

def insert_tolog(file,st,ed):
	f = open(file)
	datas = json.load(f)
	f.close()
	for data in datas:
		del(data["_id"])
		db.timeoutlog.insert(data)
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
	  	# ip_data = {"floor":ip_data["floor"], "pcwl_id":ip_data["pcwl_id"]}
	  	ip_data["log_key"] = str(ip_data["floor"]) + "-" + str(ip_data["pcwl_id"])

	  # datas = db.timeoutlog.find()
	  # for data in datas:
	  # 	data["datetime"] = dt_from_14digits_to_iso(str(data["datetime"]))
	  # 	db.timeoutlog.save(data)

	  # while (lt <= iso_ed):
	  # 	for ip_data in ip_list:
	  # 		count_sum = db.timeoutlog.find({"datetime":{"$gte":gte,"$lt":lt},"timeout_ip":ip_data["ip"]}).count()
	  # 		hourly_data = {"pcwl_id":ip_data["pcwl_id"],
	  # 									 "floor":ip_data["floor"],
	  # 									 "datetime":gte,
	  # 									 "count_sum":count_sum
	  # 									}
	  # 		db.hourlytolog.insert(hourly_data)
	  # 		count_sum = db.timeoutlog.find({"datetime":{"$gte":gte,"$lt":lt},"timeout_ip":ip_data}).count()



	  # 	gte = shift_hours(gte,1)
	  # 	lt  = shift_hours(gte,1)

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



