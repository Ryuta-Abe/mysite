# -*- coding: utf-8 -*-
# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from pymongo import *
from datetime import datetime
from convert_datetime import dt_to_end_next05,dt_from_14digits_to_iso,shift_seconds
from examine_route  import *
from get_coord import get_analy_coord 
from convert_to_mac import convert_to_mac
from statistics import mean
client = MongoClient()
db = client.nm4bd

"""
# 1. get_start_endを回し、pfvmacinfo, staymacinfoデータをDBに入れる
# 
# 2. 実験の条件をformatに従って "CSV形式" で作成する 
#    (exp_id, mac, floor, st_node, ed_node, common_dt, st_dt, ed_dt, via_nodes_list, via_dts_list, stay_pos_list)
# 
# 3. mongoimport -d nm4bd -c csvtest --headerline --columnsHaveTypes --type=csv exp_param.csv --drop
#    上記コマンドでCSVファイルをDBに取り込む。 (--dropオプションを利用可)
# 
# 4. 全データを解析すると時間がかかるので、 query に条件を入れて件数を絞ると良い
#    (exp_idに関して正規表現{"$regex":xxx}を使うと便利)
# 
# 5. python csv_examine_route.py で実行
# (! debug用のprint文は、
# 　　　examine_route.py の DEBUG_PRINT = True とすると使える)
# 
"""

## 直接実行前に指定 ##
DROP_DP = True # 過去の結果を削除するか
date = "190413"  # 解析日時()
st_exp_id = 1
ed_exp_id = 96
common_exp_id = date + "_"
err_dist_file_name = "err_dist_report.csv"  # PRデータの取得間隔毎の誤差距離の出力ファイル名
ANALYZE_MODE = False  # PRデータの取得間隔毎の誤差距離の統計を出力したい時にTrue
####################
if DROP_DP:
	db.examine_summary.drop()
	db.examine_route.drop()
	db.analy_coord.drop()

def make_exp_id(common_exp_id, st_exp_id, ed_exp_id):
	query_list = []
	for i in range(st_exp_id,ed_exp_id + 1):
		exp_num = ("000" + str(i))[-3:]
		exp_id  = common_exp_id + exp_num
		query = {"exp_id" : exp_id}
		query_list.append(query)
	return query_list

def csv_examine_route(query_list):
	for query in query_list:
		# 解析データに基づく、examine_routeに必要な正解座標を作る場合は　get_analy_coord　を使う
		# {"mac","floor","datetime","pos_x","pos_y","position","mlist"}
		get_analy_coord(query,)

		# 評価のみの場合は下の行のみ実行
		query_examine_route(query)

	# PRデータの取得間隔毎の誤差距離の統計を出力したい時に実行
	if ANALYZE_MODE:
		analyze_err_dist()

def query_examine_route(query):
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
		if isinstance(mac,int):
			mac = convert_to_mac(mac)
		floor = data[i]["floor"]
		st_node = data[i]["st_node"]
		ed_node = data[i]["ed_node"]
		exp_id = data[i]["exp_id"]

		if len(data[i]["via_nodes_list"]) == 2 or len(data[i]["via_nodes_list"]) == 0:  # [](空の場合)
			via_nodes_list = []
		else:
			via_nodes_list = list(map(int,data[i]["via_nodes_list"].split("[")[1].split("]")[0].split(",")))  # "[2,3]" → [2,3]
		
		common_dt = str(data[i]["common_dt"]) # 測定時刻における先頭の共通部分
		st_dt = dt_from_14digits_to_iso(common_dt + str(data[i]["st_dt"]))
		ed_dt = dt_from_14digits_to_iso(common_dt + str(data[i]["ed_dt"]))
		if len(data[i]["via_dts_list"]) == 2 or len(data[i]["via_dts_list"]) == 0:
			via_dts_list = []
		else:
			via_dts_list = list(data[i]["via_dts_list"].split("[")[1].split("]")[0].split(","))

		print("== exp_id:" + str(exp_id) + " ==\nmac:" + str(mac) + "\nst:" + str(st_dt) + "\ned:" + str(ed_dt))
		for j in range(len(via_dts_list)):
			via_dts_list[j] = dt_from_14digits_to_iso(common_dt + str(via_dts_list[j]))

		if ":" in data[i]["stay_pos_list"]:  # 2:1等→st_node,ed_nodeを2:1に内分する点
			ratio1 = float(data[i]["stay_pos_list"].split(":")[0])
			ratio2 = float(data[i]["stay_pos_list"].split(":")[1])
			stay_pos_list = get_dividing_point(floor,st_node,ratio1,ratio2,ed_node)
		elif len(data[i]["stay_pos_list"]) == 2 or len(data[i]["stay_pos_list"]) == 0:  # [](空の場合)
			stay_pos_list = []
		else:  # position指定  ex: [2,12.5,21.6,5]
			temp_list = data[i]["stay_pos_list"].split("[")[1].split("]")[0].split(",")
			stay_pos_list = [0,0.0,0.0,0]
			stay_pos_list = [int(temp_list[x]) if x == 0 or x == 3 else float(temp_list[x]) for x in range(len(temp_list))]
			# for x in range(len(temp_list)):
			# 	if x == 0 or x == 3:
			# 		stay_pos_list[x] = int(temp_list[x])
			# 	elif x == 1 or x == 2:
			# 		stay_pos_list[x] = float(temp_list[x])
		examine_route(mac,floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list,stay_pos_list,query)
		print("---------------------------------------------")

	def analyze_err_dist():
		examine_route_info = db.examine_route.find()
		data_count = 0
		exist_data_list = []
		for examine_data in examine_route_info:
			if(examine_data["err_dist"] != null):
				exist_data_list.append(int(examine_data["err_dist"]))
			else:
				print("null")
		average_distance = mean(exist_data_list)
		os.command("mongoexport -d nm4bd -c examine_route --type=csv -o " + err_dist_file_name + " -f err_dist,position,analyzed,mac,datetime")

if __name__ == '__main__':
	query_list = make_exp_id(common_exp_id, st_exp_id, ed_exp_id)
	csv_examine_route(query_list)
	

	# 結果を出力
	path = "../../working/"
	output_file_name = "20" + date + ".csv"
	output_file = path + output_file_name
	command = 'mongoexport --sort {"exp_id":1} -d nm4bd -c examine_summary -o '+output_file+' --type=csv --fieldFile ../../mlfile/txt/exp_result.txt'
	os.system(command)