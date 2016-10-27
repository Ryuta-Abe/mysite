import sys
from pymongo import *
from datetime import datetime
from convert_datetime import dt_to_end_next05,dt_from_14digits_to_iso,shift_seconds
client = MongoClient()
db = client.nm4bd

# CONST
MATCH_NODE_THRESHOLD = 100
UPDATE_INTERVAL = 5


def find_closest_nodes(dlist,delta_distance):
	tmp_distance = 0 # 一次保存用
	next_distance = 0 # 計算した場所から次ノードまでの距離
	prev_distance = 0 # 計算した場所から前ノードまでの距離
	for i in range(len(dlist)):
		tmp_distance += dlist[i]["distance"]
		if tmp_distance >= delta_distance:
			next_distance = tmp_distance - delta_distance
			prev_distance = dlist[i]["distance"] - next_distance
			if next_distance < MATCH_NODE_THRESHOLD:
				return [dlist[i]["direction"][1]]
			elif prev_distance < MATCH_NODE_THRESHOLD:
				return [dlist[i]["direction"][0]]
			else:
				return dlist[i]["direction"]
	# print("couldn't find nodes!") # 例外処理（delta_distanceが大きすぎる）
	return [dlist[-1]["direction"][1]]



def generate_ideal_nodes(floor,st_node,ed_node,st_dt,ed_dt):
	
	ideal_one_route = {}
	total_distance = 0
	delta_distance = 0
	velocity = 0
	nodes = []
	temp_dlist = []
	dlist = []

	ideal_one_route = db.idealroute.find_one({"$and": [{"floor" : floor},{"query" : st_node},{"query" : ed_node}]})

	if ideal_one_route["query"][0] != st_node:
	    temp_dlist = ideal_one_route["dlist"]
	    for i in range(-1,-len(dlist)-1,-1):
	        dlist.append({"direction":[tmp_dlist[i]["direction"][1],tmp_dlist[i]["direction"][0]],"distance":temp_dlist[i]["distance"]})
	else:
		dlist =  ideal_one_route["dlist"]
	total_distance = ideal_one_route["total_distance"]
	velocity = total_distance / (ed_dt - st_dt).seconds
	print(velocity)
	# tmp_distance = dlist[0]["distance"]

	st_next05_dt = dt_to_end_next05(st_dt,"iso")
	delta_distance = velocity * (st_next05_dt - st_dt).seconds
	print(delta_distance)
	nodes = find_closest_nodes(dlist,delta_distance)
	db.examine_route.insert({"datetime":st_next05_dt,"nodes":nodes})

	while st_next05_dt <= shift_seconds(ed_dt,-UPDATE_INTERVAL):
		delta_distance += velocity * UPDATE_INTERVAL
		nodes = find_closest_nodes(dlist,delta_distance)
		st_next05_dt = shift_seconds(st_next05_dt,UPDATE_INTERVAL)
		print(st_next05_dt)
		db.examine_route.insert({"datetime":st_next05_dt,"nodes":nodes})
		
	
def examine_route(floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list):
	# st_dt = dt_to_end_next05(st_dt,"iso")
	# ed_dt = dt_to_end_next05(ed_dt,"iso")
	via_num = len(via_nodes_list)
	if via_num == 0:
		generate_ideal_nodes(floor,st_node,ed_node,st_dt,ed_dt)

	else:
		generate_ideal_nodes(floor,st_node,via_nodes_list[0],st_dt,via_dts_list[0])
		for i in range(via_num - 1):
			generate_ideal_nodes(floor,via_nodes_list[i],via_nodes_list[i+1],via_dts_list[i],via_dts_list[i+1])
		generate_ideal_nodes(floor,via_nodes_list[-1],ed_node,via_dts_list[-1],ed_dt)

if __name__ == '__main__':
	# param = sys.argv
	# floor = param[1]
	# st_node = param[2][0]
	# ed_node = param[2][1]
	# via_nodes_list = param[3]
	# common_dt = str(param[4])
	# st_dt = dt_from_14digits_to_iso(common_dt + str(param[5][0]))
	# ed_dt = dt_from_14digits_to_iso(common_dt + str(param[5][1]))
	# via_dts_list = []
	# for i in len(param[6]):
	# 	via_dts_list.append(dt_from_14digits_to_iso(common_dt+str(param[6][1])))
	db.examine_route.remove({})
	floor = "W2-6F"
	st_node = 1
	ed_node = 16
	via_nodes_list = [5,8]
	st_dt = dt_from_14digits_to_iso("20161025102609")
	ed_dt = dt_from_14digits_to_iso("20161025102812")
	via_dts_list = [dt_from_14digits_to_iso("20161025102641"),dt_from_14digits_to_iso("20161025102730")]
	examine_route(floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list)

# debug用
# py examine_route.py "W2-6F" [1,16] [5,8] 2016102510 [2609,2812] [2641,2730]




