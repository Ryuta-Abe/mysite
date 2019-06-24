# -*- coding: utf-8 -*-

"""
pfvmacinfo(移動経路データ{"route":[[1 2][3 4]]), staymacinfo(滞留位置データ)を用いて、
誤差距離の算出に必要な測位位置 positionや marginをDB:analy_coordに追加する
"""
from datetime import datetime
from convert_datetime import *
from pymongo import *
from Class import Position
from math import sqrt
client = MongoClient()
db = client.nm4bd

mac = "00:11:81:10:01:1c"
floor = "W2-7F"
st_dt = 20161020134250
# st_dt = 20161020134325
# ed_dt = 20161020134430
ed_dt = 20161020134630

# db.analy_coord.remove({})

# Trueの場合, 1つ前の時刻(stay)を考慮する
CONSIDER_BEFORE = True

def get_analy_coord(query_id):
	# 解析データ抽出クエリ
	# query = {"exp_id":"161020"}
	data = db.csvtest.find_one(query_id)
	mac = data["mac"]
	floor = data["floor"]
	st_node = data["st_node"]
	ed_node = data["ed_node"]
	exp_id = data["exp_id"]

	common_dt = str(data["common_dt"]) # 測定時刻における先頭の共通部分
	st_dt = dt_from_14digits_to_iso(common_dt + str(data["st_dt"]))
	if not (str(data["st_dt"])[-1] == "0" or str(data["st_dt"])[-1] == "5"): # 測定開始時刻が5sおきの時刻でない場合
		st_dt = dt_to_end_next05(st_dt,"iso") # 今度現れる5sおきの時刻を用いる
	ed_dt = dt_from_14digits_to_iso(common_dt + str(data["ed_dt"]))
	# print("== exp_id:" + str(exp_id) + " ==\nmac:" + str(mac) + "\nst:" + str(st_dt) + "\ned:" + str(ed_dt))

	while (st_dt <= ed_dt):
		# print("--- " + str(st_dt) + " ---")
		get_coord_from_info(floor, mac, st_dt)
		st_dt = shift_seconds(st_dt, 5)

def get_coord_from_info(floor, mac, dt):
	bfr_5s = shift_seconds(dt, -5)
	query = {"floor":floor, "mac":mac, "datetime":dt}
	q_bfr = {"floor":floor, "mac":mac, "datetime":bfr_5s}
	flowdata = db.pfvmacinfo.find_one(query)
	staydata = db.staymacinfo.find_one(query)
	stay_bfr = db.staymacinfo.find_one(q_bfr)

	if (flowdata != None):
		node_num = flowdata["route"][-1][1] 
		insert_coord_from_node(floor, mac, node_num, dt)
		if (CONSIDER_BEFORE and stay_bfr != None):  # 直前がstayで、その後flowの場合、中点を測位位置とする
			node_num_bfr = stay_bfr["pcwl_id"]
			mid_coord_dict, position, mlist = get_midpoint(floor, node_num_bfr, node_num)
			db.analy_coord.update({"mac":mac,"floor":floor,"datetime":dt},
                                  {"$set": {"pos_x":mid_coord_dict["pos_x"],
								  "pos_y":mid_coord_dict["pos_y"],
								  "position":position,
								  "mlist":mlist}}, True)
	elif (staydata != None):
		node_num = staydata["pcwl_id"]
		insert_coord_from_node(floor, mac, node_num, dt)
	else:
		pass

def insert_coord_from_node(floor, mac, node_num, dt):
	from examine_route import rounding
	node_info = db.pcwlnode.find_one({"floor":floor, "pcwl_id":node_num})
	next_list = node_info["next_id"]
	next_num  = next_list[0]
	node_next = db.pcwlnode.find_one({"floor":floor, "pcwl_id":next_num})
	next_dist = db.idealroute.find_one({"$and": [{"floor" : floor},
										{"query" : node_num}, {"query" : next_num}]})["total_distance"]

	position = [node_num, 0, next_dist, next_num]
	mlist = []  # marginの位置のlist
	for n_node in next_list:
		distance = get_distance(floor, node_num, n_node)
		margin = distance/4
		mag_pos = [node_num, rounding(margin,1), rounding(distance-margin,1), n_node]
		p_x, p_y = get_position(floor, mag_pos)
		margin_dist = {"margin":margin, "pos":mag_pos, "pos_x":p_x, "pos_y":p_y}
		mlist.append(margin_dist)

	coord_data = {"mac":mac,"floor":floor,"datetime":dt,"pos_x":node_info["pos_x"],"pos_y":node_info["pos_y"],
				"position":position,"mlist":mlist}
	# print(coord_data)
	db.analy_coord.insert(coord_data)

def get_midpoint(floor, all_st_num, all_ed_num):
	from examine_route import rounding
	route_info = db.idealroute.find_one({"$and": [{"floor" : floor},
										{"query" : all_st_num},{"query" : all_ed_num}]})
	total_d = route_info["total_distance"]
	mid_len = total_d / 2

	path_list = []
	if (route_info["dlist"][0]["direction"][0] != all_st_num): ## ex: all_ed_num = 5, [0]["direction"][0] = 5
		route_info["dlist"].reverse()
		for path in route_info["dlist"]:
			path["direction"].reverse()
	for path in route_info["dlist"]:		
		path_list.append(path["direction"])

	# get midpoint
	rem_len = mid_len
	for path in route_info["dlist"]:  # 全経路の中点を含むようなpathを探索
		ref_len = path["distance"]
		st_node = db.pcwlnode.find_one({"floor":floor, "pcwl_id":path["direction"][0]})
		ed_node = db.pcwlnode.find_one({"floor":floor, "pcwl_id":path["direction"][1]})

		st_x, st_y = st_node["pos_x"],st_node["pos_y"]
		ed_x, ed_y = ed_node["pos_x"],ed_node["pos_y"]
		if (ref_len >= rem_len):
			mid_coord_dict = {"pos_x":((ref_len - rem_len)*st_x + rem_len*ed_x) / ref_len,
						 	  "pos_y":((ref_len - rem_len)*st_y + rem_len*ed_y) / ref_len
						 	 }

			mid_coord_dict["pos_x"] = rounding(mid_coord_dict["pos_x"],1)
			mid_coord_dict["pos_y"] = rounding(mid_coord_dict["pos_y"],1)
			position = [st_node["pcwl_id"], rounding(rem_len,1), rounding(path["distance"]-rem_len,1), ed_node["pcwl_id"]]
			break
		else:
			rem_len = rem_len - path["distance"]

	# get quarter-point
	margin = total_d / 4
	# quarter 1st and quarter 3rd
	margin_list = [margin, total_d - margin]
	mlist = []
	for mgn_len in margin_list:
		via_list = []
		rem_len = mgn_len
		for path in route_info["dlist"]:
			ref_len = path["distance"]
			st_node = db.pcwlnode.find_one({"floor":floor, "pcwl_id":path["direction"][0]})
			ed_node = db.pcwlnode.find_one({"floor":floor, "pcwl_id":path["direction"][1]})
			st_num = st_node["pcwl_id"]
			ed_num = ed_node["pcwl_id"]
			if (st_num not in via_list and st_num != all_st_num):
				via_list.append(st_num)
			if (ed_num not in via_list and ed_num != all_ed_num):
				via_list.append(ed_num)

			st_x, st_y = st_node["pos_x"],st_node["pos_y"]
			ed_x, ed_y = ed_node["pos_x"],ed_node["pos_y"]
			if (ref_len >= rem_len):
				mag_coord_dict = {"pos_x":((ref_len - rem_len)*st_x + rem_len*ed_x) / ref_len,
							 	  "pos_y":((ref_len - rem_len)*st_y + rem_len*ed_y) / ref_len}

				mag_coord_dict["pos_x"] = rounding(mag_coord_dict["pos_x"],1)
				mag_coord_dict["pos_y"] = rounding(mag_coord_dict["pos_y"],1)
				mag_pos = [st_node["pcwl_id"], rounding(rem_len,1), rounding(path["distance"]-rem_len,1), ed_node["pcwl_id"]]
				break
			else:
				rem_len = rem_len - path["distance"]

		p_x, p_y = get_position(floor, mag_pos)
		margin_dist = {"margin":margin, "pos":mag_pos, "pos_x":p_x, "pos_y":p_y}
		mlist.append(margin_dist)

	m_edge_list = []
	for mag_data in mlist:
		m_edge_list.append([mag_data["pos"][0], mag_data["pos"][3]])
	if (m_edge_list[0] != m_edge_list[1]):
		plist = []
		via_list = [m_edge_list[0][1], m_edge_list[1][0]]
		if (via_list[0] == via_list[1]):
			via_list.remove(via_list[1])

		# get_via_point
		tmp_path_list = []
		for via_num in via_list:
			via_node = db.pcwlnode.find_one({"floor":floor, "pcwl_id":via_num})
			for next_num in via_node["next_id"]:
				tmp_path_list.append([via_node["pcwl_id"], next_num])



		# make path_list (マージン内に存在する交差点から延びる経路の中で、移動経路と不一致の経路のみ追加)
		for tmp_path in path_list:
			rev_path = list(tmp_path)
			rev_path.reverse()
			if (tmp_path in tmp_path_list):
				tmp_path_list.remove(tmp_path)
			if (rev_path in tmp_path_list):
				tmp_path_list.remove(rev_path)

		for tmp_path in tmp_path_list:
			distance = get_distance(floor, tmp_path[0], tmp_path[1])
			mag_pos = [tmp_path[0], 0, distance, tmp_path[1]]
			p_x, p_y = get_position(floor, mag_pos)
			margin_dist = {"margin":0, "pos":mag_pos, "pos_x":p_x, "pos_y":p_y}
			mlist.append(margin_dist)

	return mid_coord_dict, position, mlist

def get_distance(floor, node1, node2):
	if node1 == node2:
		distance = 0
	else:
		route_info = db.idealroute.find_one({"$and": [{"floor" : floor},
											{"query" : node1},{"query" : node2}]})
		distance = route_info["total_distance"]
	return distance

def get_position(floor,position_list):
	prev_node,prev_distance,next_distance,next_node = position_list
	prev_node = db.pcwlnode.find_one({"floor" : floor,"pcwl_id":prev_node})
	prev_pos_x = prev_node["pos_x"]
	prev_pos_y = prev_node["pos_y"]
	next_node = db.pcwlnode.find_one({"floor" : floor,"pcwl_id":next_node})
	next_pos_x = next_node["pos_x"]
	next_pos_y = next_node["pos_y"]

	delta_x = abs(prev_pos_x - next_pos_x)
	if delta_x == 0:
		pos_x = prev_pos_x
	else:
		pos_x = (prev_pos_x * next_distance + next_pos_x * prev_distance) / (prev_distance + next_distance)
	
	delta_y = abs(prev_pos_y - next_pos_y)
	if delta_y == 0:
		pos_y = prev_pos_y
	else:
		pos_y = (prev_pos_y * next_distance + next_pos_y * prev_distance) / (prev_distance + next_distance)

	return pos_x, pos_y

def get_dividing_point(floor,prev_node,prev_ratio,next_ratio,next_node):
	# below: returns pos_x, pos_y ver.
	# prev_node_info = db.pcwlnode.find_one("floor":floor,"pcwl_id":prev_node)
	# next_node_info = db.pcwlnode.find_one("floor":floor,"pcwl_id":next_node)
	# prev_node_pos_x = prev_node_info["pos_x"]
	# prev_node_pos_y = prev_node_info["pos_y"]
	# next_node_pos_x = next_node_info["pos_x"]
	# next_node_pos_y = next_node_info["pos_y"]
	# pos_x = (prev_node_pos_x * next_ratio + next_node_pos_x * prev_ratio) / (prev_ratio + next_ratio)
	# pos_y = (prev_node_pos_y * next_ratio + next_node_pos_y * prev_ratio) / (prev_ratio + next_ratio)
	# return pos_x,pos_y
	distance = db.idealroute.find_one({"$and": [{"floor" : floor},
										{"query" : prev_node}, {"query" : next_node}]})["total_distance"]
	prev_distance = distance * prev_ratio / (prev_ratio + next_ratio)
	next_distance = distance * next_ratio / (prev_ratio + next_ratio)
	return [prev_node,prev_distance,next_distance,next_node]


def get_distance_between_points(floor,position_list1,position_list2,is_Position_Class = False):
	"""
	2点間の距離を算出するとともに、最小ルートの向きを求める
	@return[0] distance: 最小距離
	@return[1] route_index: 最小ルートがどのようなルートか
	position_list1 = P(A1,prev1,next1,B1), position_list2 = Q(A2,prev2,next2,B2)
	-4: B1 = B2の時　　　　　　 A1-P-B1====B2-Q-A2
	-3: A1 = B2の時　　　　　　 B1-P-A1====B2-Q-A2
	-2: B1 = A2の時　　　　　　 A1-P-B1====A2-Q-B2
	-1: A1 = A2の時　　　　　　 B1-P-A1====A2-Q-B2
	0: 同一線分上に存在(A1=A2とA1=B2のパターン有り)
	1:同一経路上に⇒のように並ぶ B1-P-A1----A2-Q-B2
	2:同一経路上に⇒のように並ぶ A1-P-B1----A2-Q-B2
	3:同一経路上に⇒のように並ぶ B1-P-A1----B2-Q-A2
	4:同一経路上に⇒のように並ぶ A1-P-B1----B2-Q-A2
	"""
	if is_Position_Class:
		position_list1 = position_list1.position
		position_list2 = position_list2.position
	prev1_prev2 = 0
	next1_prev2 = 0
	prev1_next2 = 0
	next1_next2 = 0
	prev_node1,prev_distance1,next_distance1,next_node1 = position_list1
	prev_node2,prev_distance2,next_distance2,next_node2 = position_list2
	if prev_node1 == prev_node2 and next_node1 == next_node2:
		distance = abs(prev_distance1 - prev_distance2)
		return distance, 0
	if prev_node1 == next_node2 and prev_node2 == next_node1:
		distance = abs(prev_distance1 - next_distance2)
		return distance, 0
	else:
		prev1_prev2 = prev_distance1 + get_distance(floor, prev_node1, prev_node2) + prev_distance2
		next1_prev2 = next_distance1 + get_distance(floor, next_node1, prev_node2) + prev_distance2
		prev1_next2 = prev_distance1 + get_distance(floor, prev_node1, next_node2) + next_distance2
		next1_next2 = next_distance1 + get_distance(floor, next_node1, next_node2) + next_distance2
		distance_list = [prev1_prev2, next1_prev2, prev1_next2, next1_next2]
		distance = min(distance_list)
		if (get_distance(floor, prev_node1, prev_node2) == 0):
			route_index = -1
		elif (get_distance(floor, next_node1, prev_node2) == 0):
			route_index = -2
		elif (get_distance(floor, prev_node1, next_node2) == 0):
			route_index = -3
		elif (get_distance(floor, next_node1, next_node2) == 0):
			route_index = -4
		else:
			route_index = distance_list.index(distance) + 1
		return distance, route_index 
	# dist_list = [prev_prev, next_prev, prev_next, next_next]
	# min_dist = min(dist_list)
	# min_index = dist_list.index(min_dist)
	# if min_index == 0 or min_index == 1:
	# 	return min_dist,"prev"
	# elif min_index == 2 or min_index == 3:
	# 	return min_dist,"next"
	# else:
	# 	print("二点間の距離の計算失敗")
	# 	return 0,None

def get_direct_distance_between_points(pos_x1,pos_y1,pos_x2,pos_y2):
	return sqrt((pos_x1 - pos_x2)^2 + (pos_y1 - pos_y2)^2)

if __name__ == '__main__':
	st_dt = dt_from_14digits_to_iso(st_dt)
	tmp_dt = st_dt
	ed_dt = dt_from_14digits_to_iso(ed_dt)
	while (tmp_dt < ed_dt):
		print("--- " + str(tmp_dt) + " ---")
		get_coord_from_info(floor, mac, tmp_dt)
		tmp_dt = shift_seconds(tmp_dt, 5)
