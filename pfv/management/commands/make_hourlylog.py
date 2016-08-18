# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from pymongo import *
from mongoengine import *
from pfv.models import timeoutlog, pcwliplist, tmptolog, hourlytolog
from pfv.convert_datetime import *

# mongoDBに接続
client = MongoClient()
db = client.nm4bd

##### hourlytolog 作成手順 #####
# 0.logを作る日時をiso_st,edに指定
# 1.key一覧取得
#   mongo nm4bd --quiet --eval "for (key in db.hourlytolog.findOne()) print(key)" > fields.txt
# 2.フィールド一覧ソート
#   py txt_sort.py fields.txt
# 3.不要なフィールド(_id等)削除 & datetime先頭に移動
# 4.mongoexport実行
#   mongoexport --sort {"datetime":1} -d nm4bd -c hourlytolog -o hourlytolog.csv --csv --fieldFile fields.txt
class Command(BaseCommand):
  help = u'aggregate timeout-logs'

  def handle(self, *args, **options):
  	# hourly aggregate
	  db.hourlytolog.remove({})
	  iso_st = dt_from_14digits_to_iso("20160817180000")
	  iso_ed = dt_from_14digits_to_iso("20160818190000")
	  print(iso_st)
	  print(iso_ed)
	  gte = iso_st
	  lt  = shift_hours(gte, 1)
	  ip_list = []
	  ip_list += db.pcwliplist.find()
	  for ip_data in ip_list:
	  	# ip_data = {"floor":ip_data["floor"], "pcwl_id":ip_data["pcwl_id"]}
	  	ip_data["log_key"] = str(ip_data["floor"]) + "-" + str(ip_data["pcwl_id"])

	  datas = db.timeoutlog.find()
	  for data in datas:
	  	data["datetime"] = dt_from_14digits_to_iso(str(data["datetime"]))
	  	db.timeoutlog.save(data)

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
