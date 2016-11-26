# -*- coding: utf-8 -*-
from datetime import datetime
from convert_datetime import *
from pymongo import *
from examine_route import *
client = MongoClient()
db = client.nm4bd

mac = "00:11:81:10:01:1c"
floor = "W2-7F"
st_dt = 20161020134250
# st_dt = 20161020134325
# ed_dt = 20161020134430
ed_dt = 20161020134630

db.analy_coord.remove({})

# Trueの場合, 1つ前の時刻(stay)を考慮する
CONSIDER_BEFORE = True

def get_analy_coord(query_id):
	datas = []
	# 解析データ抽出クエリ
	# query = {"exp_id":"161020"}
	datas += db.csvtest.find(query_id)
	for data in datas:
		mac = data["mac"]
		floor = data["floor"]
		st_node = data["st_node"]
		ed_node = data["ed_node"]
		exp_id = data["exp_id"]

		common_dt = str(data["common_dt"]) # 測定時刻における先頭の共通部分
		st_dt = dt_from_14digits_to_iso(common_dt + str(data["st_dt"]))
		tmp_dt = st_dt
		ed_dt = dt_from_14digits_to_iso(common_dt + str(data["ed_dt"]))
		# print("== exp_id:" + str(exp_id) + " ==\nmac:" + str(mac) + "\nst:" + str(st_dt) + "\ned:" + str(ed_dt))

		while (tmp_dt < ed_dt):
			# print("--- " + str(tmp_dt) + " ---")
			get_coord_from_info(floor, mac, tmp_dt)
			tmp_dt = shift_seconds(tmp_dt, 5)

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
		if (CONSIDER_BEFORE and stay_bfr != None):
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
	mlist = []
	for n_node in next_list:
		distance = get_distance(floor, node_num, n_node)
		margin = distance/4
		margin_dist = {"margin":margin, "pos":[node_num, rounding(margin,1), rounding(distance-margin,1), n_node]}
		# margin_dist = {"margin":margin, "pos":[node_num, margin, distance-margin, n_node]}
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
	if (route_info["dlist"][0]["direction"][0] != all_st_num):
		route_info["dlist"].reverse()
		for path in route_info["dlist"]:
			path["direction"].reverse()
	for path in route_info["dlist"]:		
		path_list.append(path["direction"])

	# get midpoint
	rem_len = mid_len
	for path in route_info["dlist"]:
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
			# position = [st_node, rem_len, path["distance"]-rem_len, ed_node]
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

		margin_dist = {"margin":margin, "pos":mag_pos}
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



		# make path_list (移動経路と不一致の経路のみ)
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
			margin_dist = {"margin":0, "pos":mag_pos}
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


if __name__ == '__main__':
	st_dt = dt_from_14digits_to_iso(st_dt)
	tmp_dt = st_dt
	ed_dt = dt_from_14digits_to_iso(ed_dt)
	while (tmp_dt < ed_dt):
		print("--- " + str(tmp_dt) + " ---")
		get_coord_from_info(floor, mac, tmp_dt)
		tmp_dt = shift_seconds(tmp_dt, 5)
