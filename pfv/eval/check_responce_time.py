# -*- coding: utf-8 -*-
# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from pymongo import *
from convert_datetime import *

# mongoDBに接続
client = MongoClient()
db = client.nm4bd

##### 作成手順 #####
# 1. to_check, to_check_errにインポート
# 2. py check_responce_time.py

# ("fields.txt"が存在しない場合は3-5を行う)
# 3.key一覧取得
#   mongo nm4bd --quiet --eval "for (key in db.hourlytolog.findOne()) print(key)" > fields.txt
# 4.フィールド一覧ソート
#   py txt_sort.py fields.txt
# 5.不要なフィールド(_id等)削除 & datetime先頭に移動

# 6.mongoexport実行
'''
  mongoexport --sort {"datetime":1} -d nm4bd -c hourly_irregular_count -o hourly_irregular_count.csv --csv --fieldFile fields.txt
  mongoexport --sort {"datetime":1} -d nm4bd -c hourly_responce_time -o hourly_responce_time.csv --csv --fieldFile fields.txt
  mongoexport --sort {"datetime":1} -d nm4bd -c hourly_all_to -o hourly_all_to.csv --csv --fieldFile fields.txt
'''

def check_responce_time():	
## 実行前に指定 ##
	iso_st = dt_from_14digits_to_iso("20170125000000")
	iso_ed = dt_from_14digits_to_iso("20170126160000")
	# hourly_irregular_count_file_name = "hourly_irregular_count_20"
	hourly_all_to_file_name = "hourly_all_to_25(long)"
	interval = 1 ## (h)

	db.hourly_irregular_count.remove()
	db.hourly_responce_time.remove()
	db.hourly_all_to.remove()

	print("from:" + str(iso_st))
	print("to  :" + str(iso_ed))
	gte = iso_st
	lt  = shift_hours(gte, interval)
	ip_list = []
	ip_list += db.pcwliplist.find({"$or":[{"floor":"W2-6F"},{"floor":"W2-7F"},{"floor":"W2-9F"}]})
	# for ip_data in ip_list:
	#     if not (ip_data["floor"] == "W2-9F" and ip_data["pcwl_id"] == 10):
	#         # ip_data = {"floor":ip_data["floor"], "pcwl_id":ip_data["pcwl_id"]}
	#         ip_data["log_key"] = str(ip_data["floor"]) + "-" + str(ip_data["pcwl_id"])

	while (lt <= iso_ed):
		print(gte)
		hourly_count_data = {}
		hourly_count_data["datetime"] = gte
		hourly_time_data = {}
		hourly_time_data["datetime"] = gte
		all_to_data = {}
		all_to_data["datetime"] = gte



		for ip_data in ip_list:
			hourly_responce_time = 0
			all_to_count = 0
			time_list = []

			key = str(ip_data["floor"]) + "-" + str(ip_data["pcwl_id"])
			ip = str(ip_data["ip"])
			regular_info = []
			regular_info += db.to_check.find({"get_time_no":{"$gte":gte,"$lt":lt},"ip":ip})
			regular_count = len(regular_info)
			irregular_count = db.to_check_err.find({"datetime":{"$gte":gte,"$lt":lt},"timeout_ip":ip}).count()
			all_to_count = irregular_count + db.to_check.find({"get_time_no":{"$gte":gte,"$lt":lt},"ip":ip,"difference":{"$gte":1.2}}).count()
			#     print(str(gte) + str(ip_data["log_key"]))
			if regular_count != 0:
				for i in range(regular_count):

				# hourly_time += regular_info[i]["difference"]
				# hourly_responce_time = hourly_time / regular_count
					# if regular_info[i]["difference"] > hourly_responce_time:
					# 	hourly_responce_time = regular_info[i]["difference"]
					# 	if hourly_responce_time > 0.5:
					# 		print("over!")
					time_list.append(regular_info[i]["difference"])

				time_list.sort()
				# print(time_list)
				count = round(regular_count / 100 * 70)
				hourly_responce_time = time_list[count]
			else:
				hourly_responce_time = None
			
			hourly_count_data[key] = irregular_count
			hourly_time_data[key] = hourly_responce_time
			all_to_data[key] = all_to_count


		db.hourly_irregular_count.insert(hourly_count_data)
		db.hourly_responce_time.insert(hourly_time_data)
		db.hourly_all_to.insert(all_to_data)

		gte = shift_hours(gte,interval)
		lt  = shift_hours(lt,interval)

	# os.system("mongoexport --sort {datetime:1} -d nm4bd -c hourly_irregular_count -o " + hourly_irregular_count_file_name + ".csv --csv --fieldFile fields.txt")
	os.system("mongoexport --sort {datetime:1} -d nm4bd -c hourly_all_to -o " + hourly_all_to_file_name + ".csv --csv --fieldFile fields.txt")


if __name__ == '__main__':
	check_responce_time()