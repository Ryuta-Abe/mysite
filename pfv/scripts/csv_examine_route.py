import sys
from pymongo import *
from datetime import datetime
from convert_datetime import dt_to_end_next05,dt_from_14digits_to_iso,shift_seconds
from examine_route  import *
from get_coord import *
client = MongoClient()
db = client.nm4bd

### How to use ###
# 1. pfvmacinfo, staymacinfoデータをDBに入れる
# 
# 2. 実験の条件をformatに従って "CSV形式" で作成する 
#    (exp_id, mac, floor, st_node, ed_node, common_dt, st_dt, ed_dt, via_nodes_list, via_dts_list)
# 
# 3. mongoimport -d nm4bd -c csvtest --headerline --type csv [CSV_File.csv] (--drop)
#    上記コマンドでCSVファイルをDBに取り込む。 (--dropオプションを利用可)
# 
# 4. 全データを解析すると時間がかかるので、 query に条件を入れて件数を絞ると良い
#    (exp_idに関して正規表現{"$regex":xxx}を使うと便利)
# 
# 5. python csv_examine_route.py で実行
# (! debug用のprint文は、
# 　　　examine_route.py の DEBUG_PRINT = True とすると使える)
# 
###################

query = {"exp_id":{"$regex":"161020_009"}}

def csv_examine_route(query=query):
	db.examine_route.drop()
	data = []
	# 解析データ抽出クエリ
	# query = {"exp_id":"161020"}
	data += db.csvtest.find(query)
	# CONST
	MATCH_NODE_THRESHOLD = 10
	UPDATE_INTERVAL = 5
	ANALYZE_LAG = 0

	for i in range(0,len(data)):
		mac = data[i]["mac"]
		floor = data[i]["floor"]
		st_node = data[i]["st_node"]
		ed_node = data[i]["ed_node"]
		exp_id = data[i]["exp_id"]

		if len(data[i]["via_nodes_list"]) == 2:
			via_nodes_list = []
		else:
			via_nodes_list = list(map(int,data[i]["via_nodes_list"].split("[")[1].split("]")[0].split(",")))
		
		common_dt = str(data[i]["common_dt"]) # 測定時刻における先頭の共通部分
		st_dt = dt_from_14digits_to_iso(common_dt + str(data[i]["st_dt"]))
		ed_dt = dt_from_14digits_to_iso(common_dt + str(data[i]["ed_dt"]))

		if len(data[i]["via_dts_list"]) == 2:
			via_dts_list = []
		else:
			via_dts_list = list(map(int,data[i]["via_dts_list"].split("[")[1].split("]")[0].split(",")))

		print("== exp_id:" + str(exp_id) + " ==\nmac:" + str(mac) + "\nst:" + str(st_dt) + "\ned:" + str(ed_dt))
		# if __name__ == '__main__':
			# db.examine_route.remove({})
		for i in range(len(via_dts_list)):
			via_dts_list[i] = dt_from_14digits_to_iso(common_dt + str(via_dts_list[i]))
			
		if len(data[i]["stay_pos_list"]) == 2:
			stay_pos_list = []
		else:
			temp_list = data[i]["stay_pos_list"].split("[")[1].split("]")[0].split(",")
			stay_pos_list = [0,0.0,0.0,0]
			stay_pos_list = [int(temp_list[x]) if x == 0 or x == 3 else float(temp_list[x]) for x in range(len(temp_list))]
			# for x in range(len(temp_list)):
			# 	if x == 0 or x == 3:
			# 		stay_positon_list[x] = int(temp_list[x])
			# 	elif x == 1 or x == 2:
			# 		stay_positon_list[x] = float(temp_list[x])

		examine_route(mac,floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,stay_pos_list,query)
		print("---------------------------------------------")

if __name__ == '__main__':
	# for x in range(17,18):
	# id_list = [12,16]
	# for x in id_list:
	for x in range(15,18):
		query_str = "161020_0"
		exp_num = ("00" + str(x))[-2:]
		# print(exp_nu
		exp_id  = query_str + exp_num
		query = {"exp_id" : exp_id}
		# 解析データによる座標を作る場合は　get_analy_coord　を使う
		get_analy_coord(query)
		# 評価のみの場合は下の行のみ実行

		csv_examine_route(query)