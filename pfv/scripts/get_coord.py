# -*- coding: utf-8 -*-
from datetime import datetime
from convert_datetime import *
from pymongo import *
from examine_route import rounding
client = MongoClient()
db = client.nm4bd

# st_dt = dt_from_14digits_to_iso(common_dt + str(data[i]["st_dt"]))
# ed_dt = dt_from_14digits_to_iso(common_dt + str(data[i]["ed_dt"]))
mac = "00:11:81:10:01:1c"
floor = "W2-7F"
st_dt = 20161020134250
# ed_dt = 20161020134400
ed_dt = 20161020134630

db.analy_coord.remove({})

def get_coord_from_info(floor, mac, dt):
	bfr_5s = shift_seconds(dt, -5)
	query = {"floor":floor, "mac":mac, "datetime":dt}
	q_bfr = {"floor":floor, "mac":mac, "datetime":bfr_5s}
	flowdata = db.pfvmacinfo.find_one(query)
	staydata = db.staymacinfo.find_one(query)
	stay_bfr = db.staymacinfo.find_one(q_bfr)

	if (flowdata != None):
		node_num = flowdata["route"][-1][1] 
		insert_coord_from_node(floor, node_num, dt)
		if (stay_bfr != None):
			node_num_dfr = stay_bfr["pcwl_id"]
			mid_coord_dict = get_midpoint(floor, node_num_dfr, node_num)
			# coord_data = {"mac":mac,"floor":floor,"datetime":dt,"pos_x":mid_coord_dict["pos_x"],"pos_y":mid_coord_dict["pos_y"]}
			# .update({"ip":ip},{"$set": {"th":time_stamp, "ip":ip}}, True)
			db.analy_coord.update({"mac":mac,"floor":floor,"datetime":dt},
								  {"$set": {"pos_x":mid_coord_dict["pos_x"], "pos_y":mid_coord_dict["pos_y"]}}, True)


	elif (staydata != None):
		node_num = staydata["pcwl_id"]
		insert_coord_from_node(floor, node_num, dt)
	else:
		pass

def insert_coord_from_node(floor, node_num, dt):
	node_info = db.pcwlnode.find_one({"floor":floor, "pcwl_id":node_num})
	# print(node_info["pcwl_id"],node_info["pos_x"],node_info["pos_y"])
	coord_data = {"mac":mac,"floor":floor,"datetime":dt,"pos_x":node_info["pos_x"],"pos_y":node_info["pos_y"]}
	db.analy_coord.insert(coord_data)

def get_midpoint(floor, st_num, ed_num):
	# node1 = db.pcwlnode.find_one({"floor":floor, "pcwl_id":st_num})
	# node2 = db.pcwlnode.find_one({"floor":floor, "pcwl_id":ed_num})
	route_info = db.idealroute.find_one({"$and": [{"floor" : floor},
										{"query" : st_num},{"query" : ed_num}]})
	total_d = route_info["total_distance"]
	mid_len = total_d / 2
	if (route_info["dlist"][0]["direction"][0] != st_num):
		route_info["dlist"].reverse()
		for path in route_info["dlist"]:
			path["direction"].reverse()

	rem_len = mid_len
	for path in route_info["dlist"]:
		ref_len = path["distance"]
		# st_node, ed_node = path["direction"]
		st_node = db.pcwlnode.find_one({"floor":floor, "pcwl_id":path["direction"][0]})
		ed_node = db.pcwlnode.find_one({"floor":floor, "pcwl_id":path["direction"][1]})
		st_x, st_y = st_node["pos_x"],st_node["pos_y"]
		ed_x, ed_y = ed_node["pos_x"],ed_node["pos_y"]
		# print(st_node, ed_node)
		if (ref_len >= rem_len):
			mid_coord_dict = {"pos_x":((ref_len - rem_len)*st_x + rem_len*ed_x) / ref_len,
						 	  "pos_y":((ref_len - rem_len)*st_y + rem_len*ed_y) / ref_len
						 	 }
			mid_coord_dict = {"pos_x":rounding(mid_coord_dict["pos_x"], 1),
						 	  "pos_y":rounding(mid_coord_dict["pos_y"], 1)
						 }
			# print(mid_coord)
			break
		else:
			rem_len = rem_len - path["distance"]

	return mid_coord_dict
	# print(route_info["dlist"])
	# print(route_info)


if __name__ == '__main__':
	st_dt = dt_from_14digits_to_iso(st_dt)
	tmp_dt = st_dt
	ed_dt = dt_from_14digits_to_iso(ed_dt)
	while (tmp_dt < ed_dt):
		print("---" + str(tmp_dt) + "---")
		get_coord_from_info(floor, mac, tmp_dt)
		tmp_dt = shift_seconds(tmp_dt, 5)
	# print(flowdata)
	# print(staydata)