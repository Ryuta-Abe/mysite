# -*- coding: utf-8 -*-
# import Env
import os, sys,math
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from pymongo import *
from datetime import datetime
from convert_datetime import dt_to_end_next05,dt_from_14digits_to_iso,shift_seconds
from get_coord import *
client = MongoClient()
db = client.nm4bd

# CONST
MATCH_NODE_THRESHOLD = 10
UPDATE_INTERVAL = 5
ANALYZE_LAG = 0
ADJACENT_FLAG = True # 分岐点以外でも隣接ノードokの条件の時True
# DEBUG_PRINT = True
DEBUG_PRINT = False
FLOOR_LIST = ["W2-6F","W2-7F","W2-8F","W2-9F","kaiyo"]

# global var.
examine_count = 0
exist_count = 0
match_count = 0
adjacent_count = 0
middle_count = 0
wrong_node_count = 0
wrong_floor_count = 0
error_distance = 0.0
direct_error_distance = 0.0
# stay_position_list: 移動実験:None,stay実験:position_list
stay_position_list = None
stay_correct_nodes = None

def examine_route(mac,floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list,stay_pos = [],query = None):
	global examine_count
	global exist_count
	global match_count
	global adjacent_count
	global middle_count
	global wrong_node_count
	global wrong_floor_count
	global error_distance
	global direct_error_distance
	global stay_position_list
	global stay_correct_nodes
	examine_count = 0
	exist_count = 0
	match_count = 0
	adjacent_count = 0
	middle_count = 0
	wrong_node_count = 0
	wrong_floor_count = 0
	error_distance = 0
	direct_error_distance = 0
	correct_answer_rate = 0
	correct_answer_rate_alt = 0
	average_error_distance = None
	average_error_distance_m = None
	average_direct_error_distance = None
	average_direct_error_distance_m = None
	if len(stay_pos) == 4:
		stay_position_list = stay_pos
	elif st_node == ed_node and len(via_dts_list) == 0:
		node_info = db.pcwlnode.find_one({"floor":floor, "pcwl_id":st_node})
		next_node = node_info["next_id"][0]
		next_dist = get_distance(floor,st_node,next_node)
		stay_position_list = [st_node,0.0,next_dist,next_node]
	else:
		stay_position_list = None

	if stay_position_list is not None:
		prev_node,prev_distance,next_distance,next_node = stay_position_list
		if prev_distance < MATCH_NODE_THRESHOLD:
			stay_correct_nodes = add_adjacent_nodes(floor,prev_node,ADJACENT_FLAG)
		elif next_distance < MATCH_NODE_THRESHOLD:
			stay_correct_nodes = add_adjacent_nodes(floor,next_node,ADJACENT_FLAG)
		else:
			stay_correct_nodes = [prev_node,next_node]
	else:
		stay_correct_nodes = None

	if query is None:
		exp_id = None
	else:
		exp_id = query["exp_id"]
	if len(via_nodes_list)== 0:
		examine_partial_route(mac,floor,st_node,ed_node,st_dt,ed_dt)

	else:
		examine_partial_route(mac,floor,st_node,via_nodes_list[0],st_dt,via_dts_list[0])
		for i in range(len(via_nodes_list) - 1):
			examine_partial_route(mac,floor,via_nodes_list[i],via_nodes_list[i+1],via_dts_list[i],via_dts_list[i+1])
		examine_partial_route(mac,floor,via_nodes_list[-1],ed_node,via_dts_list[-1],ed_dt)
	
	accuracy,existing_data_rate,average_error_distance,average_direct_error_distance, match_rate, adjacent_rate, middle_rate, wrong_node_rate  = process_count_result()
	if average_error_distance is not None:
		average_error_distance_m = rounding(average_error_distance * 14.4 / 110,2)
		average_error_distance = rounding(average_error_distance,2)
	if average_direct_error_distance is not None:
		average_direct_error_distance_m = rounding(average_direct_error_distance * 14.4 / 110,2)
	db.examine_summary.insert({"exp_id":exp_id,"mac":mac,"floor":floor,"st_node":st_node,"ed_node":ed_node,"via_nodes_list":via_nodes_list,"st_dt":st_dt,"ed_dt":ed_dt,"via_dts_list":via_dts_list,
		"accuracy":accuracy,"existing_rate":existing_data_rate,
		"avg_err_dist[px]":average_error_distance,"avg_err_dist[m]":average_error_distance_m,"avg_direct_err_dist[m]":average_direct_error_distance_m,
		"match_rate":match_rate, "adjacent_rate":adjacent_rate, "middle_rate":middle_rate, "wrong_node_rate":wrong_node_rate})

def examine_partial_route(mac,floor,st_node,ed_node,st_dt,ed_dt):
	ideal_one_route = {}
	total_distance = 0
	delta_distance = 0
	velocity = 0
	nodes = []
	temp_dlist = []
	dlist = []
	data = {}
	is_correct = False
	is_exist = False
	judgement = ""

	if stay_position_list is not None:
		if db.examine_route.find({"mac":mac,"datetime":st_dt}).count() == 0:
			st_next05_dt = dt_to_end_next05(st_dt,"iso")
			judgement = examine_position(mac,floor,st_next05_dt)
			update_partial_count(judgement)

		else:
			st_next05_dt = st_dt

		while st_next05_dt <= shift_seconds(ed_dt,-UPDATE_INTERVAL):
			st_next05_dt = shift_seconds(st_next05_dt,UPDATE_INTERVAL)
			judgement = examine_position(mac,floor,st_next05_dt)
			update_partial_count(judgement)

	else:	
		ideal_one_route = db.idealroute.find_one({"$and": [{"floor" : floor},{"query" : st_node},{"query" : ed_node}]})
		if ideal_one_route["query"][0] != st_node:
			temp_dlist = ideal_one_route["dlist"]
			for i in range(-1,-len(temp_dlist)-1,-1):
				dlist.append({"direction":[temp_dlist[i]["direction"][1],temp_dlist[i]["direction"][0]],"distance":temp_dlist[i]["distance"]})
		else:
			dlist =  ideal_one_route["dlist"]
		total_distance = ideal_one_route["total_distance"]
		velocity = total_distance / (ed_dt - st_dt).seconds
		if DEBUG_PRINT:
			print("\n" + "from " + str(st_node) + " to " + str(ed_node) + " : velocity = " + str(rounding(velocity,2)) + " [px/s]")
		if db.examine_route.find({"mac":mac,"datetime":st_dt}).count() == 0:
			st_next05_dt = dt_to_end_next05(st_dt,"iso")
			delta_distance = velocity * (st_next05_dt - st_dt).seconds
			judgement = examine_position(mac,floor,st_next05_dt,dlist,delta_distance)
			update_partial_count(judgement)
		else:
			st_next05_dt = st_dt

		while st_next05_dt <= shift_seconds(ed_dt,-UPDATE_INTERVAL):
			delta_distance += velocity * UPDATE_INTERVAL
			st_next05_dt = shift_seconds(st_next05_dt,UPDATE_INTERVAL)
			judgement = examine_position(mac,floor,st_next05_dt,dlist,delta_distance)
			update_partial_count(judgement)

def examine_position(mac,floor,dt,dlist = [],delta_distance = 0):
	global error_distance
	global direct_error_distance
	moment_direct_error_distance = 0
	real_floor = ""
	analyzed_node = 0
	correct_nodes = []
	actual_position_list = [0,0.0,0.0,0] #　計算した場所の格納用([前ノードのid,prev_distance,next_distance,次ノードのid])	
	analyzed_position_list = [0,0.0,0.0,0] 
	judgement = ""
	moment_error_dist = 0
	temp_dist = 0
	min_dist = 9999
	if stay_position_list is not None:
		actual_position_list = stay_position_list
		correct_nodes = stay_correct_nodes
	else:
		correct_nodes,actual_position_list = find_correct_nodes_and_position(floor,dlist,delta_distance)
	pos_x,pos_y = get_position(floor,actual_position_list)
	
	# get_coord_from_info(floor, mac, dt)
	analyzed_data = db.analy_coord.find_one({"datetime":dt, "mac":mac})
	if analyzed_data is None:
		judgement = "F(None)"
		moment_error_dist = None
	else:
		# real_floor = analyzed_data["floor"]
		# To Do : improve verification process by using analyzed data
		analyzed_pos_x = analyzed_data["pos_x"]
		analyzed_pos_y = analyzed_data["pos_y"]

		real_floor, analyzed_node = find_analyzed_node(mac, floor, dt)

		if real_floor != floor:
			judgement = "F("+ real_floor + ")"
			moment_error_dist = None
		
		if real_floor == floor:
			mlist = analyzed_data["mlist"]
			analyzed_position_list = analyzed_data["position"]
			# analyzed_actual_dist = get_distance_between_points(floor,analyzed_position_list,actual_position_list)
			for i in range(len(mlist)):
				# analyzed_margin_dist = get_distance_between_points(floor,analyzed_position_list,mlist[i]["pos"])
				# if analyzed_actual_dist < mlist[i]["margin"]:
				# 	moment_error_dist = 0
				# 	break
				if isinside(analyzed_data["pos_x"],pos_x,mlist[i]["pos_x"]) and isinside(analyzed_data["pos_y"],pos_y,mlist[i]["pos_y"]):
					moment_error_dist = 0
					break
				else:
					temp_dist = mlist[i]["margin"]
					temp_dist += get_distance_between_points(floor,mlist[i]["pos"],actual_position_list)
				if temp_dist < min_dist:
					min_dist = temp_dist
					moment_error_dist = rounding(min_dist - mlist[i]["margin"],2)
			error_distance += moment_error_dist

			moment_direct_error_distance = math.sqrt(pow((pos_x - analyzed_pos_x),2) + pow((pos_y - analyzed_pos_y),2))
			direct_error_distance += moment_direct_error_distance

			if not (analyzed_node in correct_nodes):
				judgement = "F(Wrong Node)"

			elif len(correct_nodes) == 2:
				judgement = "T(Middle)"

			elif analyzed_node == correct_nodes[0]:
				judgement = "T(Match)"

			else:
				judgement = "T(Adjacent)"
	db.examine_route.insert({"floor": floor, "mac": mac, "datetime":dt,"judgement":judgement,"position":actual_position_list,
		"pos_x":pos_x,"pos_y":pos_y,"correct":correct_nodes,"analyzed":analyzed_node,"err_dist":moment_error_dist,"direct_err_dist":moment_direct_error_distance})
	db.actual_position.insert({"floor": floor, "mac": mac, "datetime":dt,"pos_x":pos_x,"pos_y":pos_y})

	if DEBUG_PRINT:
		print(str(dt) + ":" + judgement,"pos:" + str(actual_position_list),"correct:" + str(correct_nodes),
			"analyzed:" + str(analyzed_node),"err_dist:" + str(moment_error_dist),end="")
		if moment_error_dist is not None:
			print("[px]")
		else:
			print("")

	return judgement

def update_partial_count(judgement):
	global examine_count
	global exist_count
	global match_count
	global adjacent_count
	global middle_count
	global wrong_node_count
	global wrong_floor_count
	
	examine_count += 1 
	exist_count += 1

	if judgement[0] == "T":
		if judgement[2:7] == "Match":
			match_count += 1
		elif judgement[2:10] == "Adjacent":
			adjacent_count += 1
		elif judgement[2:8] == "Middle":
			middle_count += 1
		else:
			print("unexpected judgement error!")
	if judgement[0] == "F":
		if judgement[2:6] == "None":
			exist_count -= 1 # とりあえず増やしたexist_countを取消
		elif judgement[2:12] == "Wrong Node":
			wrong_node_count += 1
		elif judgement[2:-1] in FLOOR_LIST:
			wrong_floor_count += 1
		else:
			print("unexpected judgement error!")

def isinside(end1_coord,target_coord,end2_coord):
	if end1_coord <= target_coord <= end2_coord or end1_coord >= target_coord >= end2_coord:
		return True
	else:
		return False

def find_analyzed_node(mac,floor,dt):
	analyzed_data = {}
	analyzed_node = 0
	same_floor_query = {"floor":floor,"datetime":dt,"mac":mac}
	all_floors_query = {"datetime":dt,"mac":mac}

	# 同一フロアのflowに解析データが存在
	analyzed_data = db.pfvmacinfo.find_one(same_floor_query)
	if analyzed_data is not None:
		analyzed_node = analyzed_data["route"][-1][1]
		return floor,analyzed_node

	# 同一フロアのstayに解析データが存在
	analyzed_data = db.staymacinfo.find_one(same_floor_query)
	if analyzed_data is not None:
		analyzed_node = analyzed_data["pcwl_id"]
		return floor,analyzed_node

	# 違うフロアのflowに解析データが存在
	analyzed_data = db.pfvmacinfo.find_one(all_floors_query)
	if analyzed_data is not None:
		analyzed_node = analyzed_data["route"][-1][1]
		floor = analyzed_data["floor"]
		return floor,analyzed_node

	# 違うフロアのstayに解析データが存在
	analyzed_data = db.staymacinfo.find_one(all_floors_query)
	if analyzed_data is not None:
		analyzed_node = analyzed_data["pcwl_id"]
		floor = analyzed_data["floor"]
		return floor,analyzed_node

	return None,None

def find_correct_nodes_and_position(floor,dlist,delta_distance):
	temp_distance = 0 # 一次保存用
	next_distance = 0 # 計算した場所から次ノードまでの距離
	prev_distance = 0 # 計算した場所から前ノードまでの距離
	correct_nodes = []
	actual_position_list = [0,0,0,0] #　計算した場所の格納用([前ノードのid,prev_distance,next_distance,次ノードのid])
	for i in range(len(dlist)):
		temp_distance += dlist[i]["distance"]
		if temp_distance >= delta_distance:
			next_distance = temp_distance - delta_distance
			prev_distance = dlist[i]["distance"] - next_distance
			if next_distance < MATCH_NODE_THRESHOLD:
				correct_nodes = add_adjacent_nodes(floor,dlist[i]["direction"][1],ADJACENT_FLAG)
				break

			elif prev_distance < MATCH_NODE_THRESHOLD:
				correct_nodes = add_adjacent_nodes(floor,dlist[i]["direction"][0],ADJACENT_FLAG)
				break

			else:
				correct_nodes = dlist[i]["direction"]
				break
	else:
		print("reached ed_node!!")	
		next_distance = 0
		prev_distance = dlist[i]["distance"]
		correct_nodes = add_adjacent_nodes(floor,dlist[i]["direction"][1],ADJACENT_FLAG)

	actual_position_list = [dlist[i]["direction"][0],rounding(prev_distance,2),rounding(next_distance,2),dlist[i]["direction"][1]]
	return correct_nodes,actual_position_list

def add_adjacent_nodes(floor,node,adjacent_flag):
	pcwlnode = {}
	adjacent_nodes = [node]

	node_info = db.pcwlnode_test.find_one({"floor":floor,"pcwl_id":node})
	adjacent_nodes.extend(node_info["next_id"])
	if len(adjacent_nodes) >= 3:
		return adjacent_nodes
	elif adjacent_flag:
		return adjacent_nodes
	else:
		return [node]

# def get_error_distance(floor,analyzed_node,actual_position_list):
# 	prev_node,prev_distance,next_distance,next_node = actual_position_list
# 	if analyzed_node == prev_node:
# 		return rounding(prev_distance,2)
# 	if analyzed_node == next_node:
# 		return rounding(next_distance,2)

# 	via_prev_distance = prev_distance
# 	via_next_distance = next_distance
# 	via_prev_query = {"$and": [{"floor" : floor},{"query" : analyzed_node},{"query" : prev_node}]}
# 	via_next_query = {"$and": [{"floor" : floor},{"query" : analyzed_node},{"query" : next_node}]}

# 	via_prev_distance += db.idealroute.find_one(via_prev_query)["total_distance"]
# 	via_next_distance += db.idealroute.find_one(via_next_query)["total_distance"]
# 	return rounding(min(via_prev_distance,via_next_distance),2)

def get_distance_between_points(floor,position_list1,position_list2):
	prev1_prev2 = 0
	next1_prev2 = 0
	prev1_next2 = 0
	next1_next2 = 0
	prev_node1,prev_distance1,next_distance1,next_node1 = position_list1
	prev_node2,prev_distance2,next_distance2,next_node2 = position_list2
	if prev_node1 == prev_node2 and next_node1 == next_node2:
		return abs(prev_distance1 - prev_distance2)
	if prev_node1 == next_node2 and prev_node2 == next_node1:
		return abs(prev_distance1 - next_distance2)
	prev1_prev2 = prev_distance1 + get_distance(floor, prev_node1, prev_node2) + prev_distance2
	next1_prev2 = next_distance1 + get_distance(floor, next_node1, prev_node2) + prev_distance2
	prev1_next2 = prev_distance1 + get_distance(floor, prev_node1, next_node2) + next_distance2
	next1_next2 = next_distance1 + get_distance(floor, next_node1, next_node2) + next_distance2
	return min(prev1_prev2, next1_prev2, prev1_next2, next1_next2)
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
	return (pos_x1 - pos_x2)^2 + (pos_y1 - pos_y2)





# rounding in specified place
def rounding(num, round_place):
	rounded_num = round(num*pow(10, round_place)) / pow(10, round_place)
	return rounded_num


def process_count_result():
	accuracy = None
	existing_accuracy = None
	existing_data_rate = None
	match_rate = 0
	adjacent_rate = 0
	middle_rate = 0
	wrong_floor_rate = 0
	wrong_node_rate = 0
	correct_count = 0
	average_error_distance = None
	average_direct_error_distance = None

	correct_count = match_count + adjacent_count + middle_count
	false_count = examine_count - correct_count



	if examine_count == 0 :
		print("--- no data!! ---")
	else:
		accuracy = rounding(correct_count / examine_count * 100, 2)
		print ("\n" + "accuracy: " + str(accuracy) + "% "
		 + "( " + str(correct_count) + " / " + str(examine_count) + " )",end="  ")


	if exist_count == 0 :
		print("--- info_data does not exist! ---")
	else:
		existing_accuracy = rounding(correct_count / exist_count * 100, 2)
		print ("accuracy(existing only): " + str(existing_accuracy) + "% "
		 + "( " + str(correct_count) + " / " + str(exist_count) + " )",end="  ")

		existing_data_rate = rounding(exist_count/examine_count * 100, 2)
		print("existing data rate: " + str(existing_data_rate) + "% "
			+ "( " + str(exist_count) + " / " + str(examine_count) + " )")
		
		average_error_distance = error_distance/exist_count
		print("average error distance: " + str(rounding(average_error_distance,2)) + "[px]")
		average_direct_error_distance = direct_error_distance / exist_count
		print("average direct error distance: " + str(rounding(average_direct_error_distance,2)) + "[px]")


		print("\n-- detail info of true results --")

		match_rate = rounding(match_count / exist_count * 100, 2)
		print ("match rate: " + str(match_rate) + "% "
		 + "( " + str(match_count) + " / " + str(exist_count) + " )",end="  ")

		adjacent_rate = rounding(adjacent_count / exist_count * 100, 2)
		print ("adjacent rate: " + str(adjacent_rate) + "% "
		 + "( " + str(adjacent_count) + " / " + str(exist_count) + " )",end="  ")

		middle_rate = rounding(middle_count / exist_count * 100, 2)
		print ("middle rate: " + str(middle_rate) + "% "
		 + "( " + str(middle_count) + " / " + str(exist_count) + " )",end="  ")

		if correct_count != 0:
			match_rate_true = rounding(match_count / correct_count * 100, 2)
			print ("match rate(true only): " + str(match_rate_true) + "% "
			 + "( " + str(match_count) + " / " + str(correct_count) + " )")

			adjacent_rate_true = rounding(adjacent_count / correct_count * 100, 2)
			print ("adjacent rate(true only): " + str(adjacent_rate_true) + "% "
			 + "( " + str(adjacent_count) + " / " + str(correct_count) + " )")

			middle_rate_true = rounding(middle_count / correct_count * 100, 2)
			print ("middle rate(true only): " + str(middle_rate_true) + "% "
			 + "( " + str(middle_count) + " / " + str(correct_count) + " )")

		print("\n-- detail info of false results --")

		wrong_floor_rate = rounding(wrong_floor_count / exist_count * 100, 2)
		print ("wrong floor rate: " + str(wrong_floor_rate) + "% "
		 + "( " + str(wrong_floor_count) + " / " + str(exist_count) + " )",end="  ")

		wrong_node_rate = rounding(wrong_node_count / exist_count * 100, 2)
		print ("wrong node rate: " + str(wrong_node_rate) + "% "
		 + "( " + str(wrong_node_count) + " / " + str(exist_count) + " )",end="  ")

		if false_count != 0:
			wrong_floor_rate_false = rounding(wrong_floor_count / false_count * 100, 2)
			print ("wrong floor rate(false only): " + str(wrong_floor_rate_false) + "% "
			 + "( " + str(wrong_floor_count) + " / " + str(false_count) + " )")
			
			wrong_node_rate_false = rounding(wrong_node_count / false_count * 100, 2)
			print ("wrong node rate(false only): " + str(wrong_node_rate_false) + "% "
			 + "( " + str(wrong_node_count) + " / " + str(false_count) + " )")


	return existing_accuracy,existing_data_rate,average_error_distance, average_direct_error_distance, match_rate, adjacent_rate, middle_rate, wrong_node_rate


# # DBに入っているデータを出力することも可能(コメント解除)
# def is_correct_node(mac,floor,dt,nodes):
# 	# dtにする
# 	analyze_time = shift_seconds(dt,ANALYZE_LAG)
# 	analyze_data = {}
# 	pfv_query  = {"floor":floor,"datetime":analyze_time,"mac":mac}
# 	stay_query = {"floor":floor,"datetime":analyze_time,"mac":mac}
# 	# print(pfv_query)
# 	pfv_query_alt  = {"datetime":analyze_time,"mac":mac}
# 	stay_query_alt = {"datetime":analyze_time,"mac":mac}

# 	for node in nodes:
# 		analyze_data = db.pfvmacinfo.find_one(pfv_query)
# 		# print(analyze_data)
# 		stay_query["pcwl_id"] = node
# 		if (analyze_data is not None and analyze_data["route"][-1][1] == node):
# 			return True,analyze_data["route"][-1][1]
# 			# return True, analyze_data["route"]
# 		elif (db.staymacinfo.find(stay_query).count() == 1):
# 			# TODO: ~.count() >= 2 pattern
# 			return True,db.staymacinfo.find_one(stay_query)["pcwl_id"]
# 			# return True, node

# 	# for node in nodes:
# 	analyze_data = db.pfvmacinfo.find_one(pfv_query)
# 	# print(analyze_data)
# 	if (analyze_data is not None):
# 		return False,analyze_data["route"][-1][1]
# 	# print(stay_query)
# 	del(stay_query["pcwl_id"])
# 	analyze_data = db.staymacinfo.find_one(stay_query)
# 	# print(analyze_data)
# 	if (analyze_data is not None):
# 		return False,analyze_data["pcwl_id"]
# 		# return False, analyze_data["route"]

# 	for node in nodes:
# 		analyze_data = db.pfvmacinfo.find_one(pfv_query_alt)
# 		stay_query_alt["pcwl_id"] = node
# 		stay_data = db.staymacinfo.find(stay_query_alt)
# 		if (analyze_data is not None):
# 			return False
# 			# return False, analyze_data["route"]
# 		elif (stay_data.count() == 1):
# 			# TODO: ~.count() >= 2 pattern
# 			return False
# 			# return False, stay_data[0]["floor"]

# 	return False, None
# 	# return False, None

# # DBにデータが入っているか確認
# def is_exist_data(mac,floor,dt,nodes):
# 	analyze_time = shift_seconds(dt,ANALYZE_LAG)
# 	query = {"floor":floor,"datetime":analyze_time,"mac":mac}
# 	if(db.pfvmacinfo.find(query).count() != 0):
# 		return True
# 	elif(db.staymacinfo.find(query).count() != 0):
# 		return True
# 	else:
# 		return False


# # judge correct, judge data exists, and insert examine_route  
# def judge_and_ins_correct_route(mac,floor,nodes,st_dt,st_next05_dt,correct_count,examine_count,exist_count):
# 	# is_correct = is_correct_node(mac,floor,st_next05_dt,nodes)
# 	is_correct, analyzed_data = is_correct_node(mac,floor,st_next05_dt,nodes)
# 	is_exist = is_exist_data(mac,floor,st_next05_dt,nodes)
# 	examine_count += 1
# 	if is_correct:
# 		correct_count += 1
# 	if is_exist:
# 		exist_count += 1
# 	db.examine_route.insert({"datetime":st_next05_dt,"nodes":nodes,"is_correct":is_correct})
# 	if DEBUG_PRINT:
# 		print(str(st_next05_dt) + " : " + str(nodes) + " , " + str(is_correct)+ " , "+ str(analyzed_data))
# 	# print("    analyzed data     " + str(analyzed_data))
# 	return correct_count, examine_count, exist_count



if __name__ == '__main__':
	### exp_info ###
	mac = "00:11:81:10:01:19"
	floor = "W2-7F"

	### flow ###
	st_node = 1
	ed_node = 1
	via_nodes_list = [5,21,17,12,9,7,5]
	common_dt = str(2016102013) # 測定時刻における先頭の共通部分
	st_dt = dt_from_14digits_to_iso(common_dt + str(5500))
	ed_dt = dt_from_14digits_to_iso(common_dt + str(5818))
	via_dts_list = [5528,5545,5613,5639,5654,5725,5749]

	### stay ###
	# mac = "00:11:81:10:01:17"
	# st_node = 5
	# ed_node = 5
	# via_nodes_list = []
	# common_dt = str(20161020) # 測定時刻における先頭の共通部分
	# st_dt = dt_from_14digits_to_iso(common_dt + str(115600))
	# ed_dt = dt_from_14digits_to_iso(common_dt + str(120920))
	# via_dts_list = []

	# db.examine_route.remove({})
	for i in range(len(via_dts_list)):
		via_dts_list[i] = dt_from_14digits_to_iso(common_dt + str(via_dts_list[i]))
	
	while (st_dt <= ed_dt):
		get_coord_from_info(floor, mac, st_dt)
		st_dt = shift_seconds(st_dt, 5)
	examine_route(mac,floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list)




