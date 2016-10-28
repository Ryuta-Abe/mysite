import sys
from pymongo import *
from datetime import datetime
from convert_datetime import dt_to_end_next05,dt_from_14digits_to_iso,shift_seconds
from examine_route  import is_correct_node,find_adjacent_nodes,find_ideal_nodes,generate_ideal_nodes,examine_route
client = MongoClient()
db = client.nm4bd
data = []
data += db.csvtest.find()
# CONST
MATCH_NODE_THRESHOLD = 10
UPDATE_INTERVAL = 5
ANALYZE_LAG = 0

for i in range(1,len(data)):
	MAC = data[i]["mac"]
	ADJACENT_FLAG = True # 分岐点以外でも隣接ノードokの条件の時True
	floor = data[i]["floor"]
	st_node = data[i]["st_node"]
	ed_node = data[i]["ed_node"]
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
	if __name__ == '__main__':
		db.examine_route.remove({})
		for i in range(len(via_dts_list)):
			via_dts_list[i] = dt_from_14digits_to_iso(common_dt + str(via_dts_list[i]))
		examine_route(floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list)