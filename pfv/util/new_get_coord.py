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
CONSIDER_BEFORE = False

MARGIN_RATIO = 4  # 中点を含めたFingerprintの際は4、ノードのみの時は2

def get_analy_coord(query_id):
	# 解析データ抽出クエリ
	# query = {"exp_id":"161020"}
	data = db.csvtest.find_one(query_id)

	mac = data["mac"]
	# floor = data["floor"]
	# st_node = data["st_node"]
	# ed_node = data["ed_node"]
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
	aft_5s = shift_seconds(dt, 5)
	bfr_5s = shift_seconds(dt, -5)
	query = {"floor":floor, "mac":mac, "datetime":{"$gte":dt,"$lt":aft_5s}}
	# q_bfr = {"floor":floor, "mac":mac, "datetime":{"$gte":bfr_5s,"$lt":dt}}
	flowdata = db.pfvmacinfo.find_one(query)
	staydata = db.staymacinfo.find_one(query)
	# stay_bfr = db.staymacinfo.find_one(q_bfr)

	if (flowdata is not None):
		position = flowdata["route"][-1][1] 
		insert_coord_from_node(floor, mac, position, dt)
		# if (CONSIDER_BEFORE and stay_bfr is not None None):  # 直前がstayで、その後flowの場合、中点を測位位置とする
		# 	position_bfr = stay_bfr["position"]
		# 	mid_coord_dict, position, mlist = get_midpoint(floor, position_bfr, position)
		# 	db.analy_coord.update({"mac":mac,"floor":floor,"datetime":dt},
        #                           {"$set": {"pos_x":mid_coord_dict["pos_x"],
		# 						  "pos_y":mid_coord_dict["pos_y"],
		# 						  "position":position,
		# 						  "mlist":mlist}}, True)
	elif (staydata is not None):
		position = staydata["position"]
		insert_coord_from_node(floor, mac, position, dt)
	else:
		print("Error:","Not found")
		pass

def insert_coord_from_node(floor, mac, position, dt):
	from examine_route import rounding
	prev_node, prev_dist, next_dist, next_node = position
	mlist = [] # marginのリスト

	def append_in_mlist(floor,margin_position,mlist,margin_dist):
		pos_x, pos_y = get_position(floor, margin_position)
		margin_dict = {"margin":margin_dist, "pos":margin_position, "pos_x":pos_x, "pos_y":pos_y}
		mlist.append(margin_dict)
		return mlist
	
	# positionがnodeの場合
	if next_dist == 0:
		position = Position(position).reverse_order()
		prev_node, prev_dist, next_dist, next_node = position
	if prev_dist == 0:  
		node_info = db.pcwlnode.find_one({"floor":floor,"pcwl_id":prev_node})
		next_list = node_info["next_id"]
		for next_node in next_list:
			distance = get_distance(floor, prev_node, next_node)
			margin = distance/MARGIN_RATIO
			mag_pos = [prev_node, margin, distance - margin, next_node]
			mlist = append_in_mlist(floor,mag_pos,mlist,margin)

	# positionがnodeでない(node間)である場合
	else: 
		route_info = db.idealroute.find_one({"$and": [{"floor" : floor},
											{"query" : prev_node}, {"query" : next_node}]})
		route_distance = route_info["total_distance"]
		margin = route_distance/ MARGIN_RATIO
		# prev側のmarginを算出
		if margin < prev_dist:  # marginがpositionの両端(prev,next_node)からはみ出ない場合
			prev_margin_prev_dist = prev_dist - margin
			prev_margin_next_dist = next_dist + margin
			mag_pos = [prev_node,prev_margin_prev_dist,prev_margin_next_dist,next_node]
			p_x, p_y = get_position(floor, mag_pos)
			margin_dict = {"margin":margin, "pos":mag_pos, "pos_x":p_x, "pos_y":p_y}
			mlist.append(margin_dict)
		else:  # marginがpositionの両端(prev,next_node)からはみ出る場合
			surplus = margin - prev_dist
			mlist = get_mlist_in_surplus(floor,prev_node,surplus,mlist,margin)
		# next側のmarginを算出
		if margin < next_dist:
			next_margin_prev_dist = prev_dist + margin
			next_margin_next_dist = next_dist - margin
			mag_pos = [prev_node,next_margin_prev_dist,next_margin_next_dist,next_node]
			p_x, p_y = get_position(floor, mag_pos)
			margin_dict = {"margin":margin, "pos":mag_pos, "pos_x":p_x, "pos_y":p_y}
			mlist.append(margin_dict)
		else:
			surplus = margin - prev_dist
			mlist = get_mlist_in_surplus(floor,prev_node,surplus,mlist,margin)
	pos_x, pos_y = get_position(floor, position)

	coord_data = {"mac":mac,"floor":floor,"datetime":dt,"pos_x":pos_x,"pos_y":pos_y,
				"position":position,"mlist":mlist}
	# print(coord_data)
	db.analy_coord.insert(coord_data)

def get_mlist_in_surplus(floor,pcwl_id,surplus,mlist,margin):
	node_info = db.pcwlnode.find_one({"floor":floor, "pcwl_id":pcwl_id})
	next_list = node_info["next_id"]
	for next_node in next_list:
		distance = get_distance(floor, pcwl_id, next_node)
		mag_pos = [pcwl_id, surplus, distance - surplus , next_node]
		p_x, p_y = get_position(floor, mag_pos)
		margin_dist = {"margin":margin, "pos":mag_pos, "pos_x":p_x, "pos_y":p_y}
		mlist.append(margin_dist)
	return mlist

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


def get_distance_between_points(floor,position_list1,position_list2,isPositionClass = False):
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
	if isPositionClass:
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
