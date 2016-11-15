import sys
from pymongo import *
from datetime import datetime
from convert_datetime import dt_to_end_next05,dt_from_14digits_to_iso,shift_seconds
client = MongoClient()
db = client.nm4bd

# CONST
MATCH_NODE_THRESHOLD = 10
UPDATE_INTERVAL = 5
ANALYZE_LAG = 0
ADJACENT_FLAG = True # 分岐点以外でも隣接ノードokの条件の時True
DEBUG_PRINT = True

# rounding in specified place
def rounding(num, round_place):
	rounded_num = round(num*pow(10, round_place)) / pow(10, round_place)
	return rounded_num

# DBに入っているデータを出力することも可能(コメント解除)
def is_correct_node(mac,floor,dt,nodes):
	analyze_time = shift_seconds(dt,ANALYZE_LAG)
	analyze_data = {}
	pfv_query  = {"floor":floor,"datetime":analyze_time,"mac":mac}
	stay_query = {"floor":floor,"datetime":analyze_time,"mac":mac}
	# print(pfv_query)
	pfv_query_alt  = {"datetime":analyze_time,"mac":mac}
	stay_query_alt = {"datetime":analyze_time,"mac":mac}

	for node in nodes:
		analyze_data = db.pfvmacinfo.find_one(pfv_query)
		# print(analyze_data)
		stay_query["pcwl_id"] = node
		if (analyze_data is not None and analyze_data["route"][-1][1] == node):
			return True,analyze_data["route"][-1][1]
			# return True, analyze_data["route"]
		elif (db.staymacinfo.find(stay_query).count() == 1):
			# TODO: ~.count() >= 2 pattern
			return True,db.staymacinfo.find_one(stay_query)["pcwl_id"]
			# return True, node

	# for node in nodes:
	analyze_data = db.pfvmacinfo.find_one(pfv_query)
	# print(analyze_data)
	if (analyze_data is not None):
		return False,analyze_data["route"][-1][1]
	# print(stay_query)
	del(stay_query["pcwl_id"])
	analyze_data = db.staymacinfo.find_one(stay_query)
	# print(analyze_data)
	if (analyze_data is not None):
		return False,analyze_data["pcwl_id"]
		# return False, analyze_data["route"]

	for node in nodes:
		analyze_data = db.pfvmacinfo.find_one(pfv_query_alt)
		stay_query_alt["pcwl_id"] = node
		stay_data = db.staymacinfo.find(stay_query_alt)
		if (analyze_data is not None):
			return False
			# return False, analyze_data["route"]
		elif (stay_data.count() == 1):
			# TODO: ~.count() >= 2 pattern
			return False
			# return False, stay_data[0]["floor"]

	return False, None
	# return False, None

# DBにデータが入っているか確認
def is_exist_data(mac,floor,dt,nodes):
	analyze_time = shift_seconds(dt,ANALYZE_LAG)
	query = {"floor":floor,"datetime":analyze_time,"mac":mac}
	if(db.pfvmacinfo.find(query).count() != 0):
		return True
	elif(db.staymacinfo.find(query).count() != 0):
		return True
	else:
		return False

def find_adjacent_nodes(floor,node,adjacent_flag):
	pcwlnode = {}
	adjacent_nodes = [node]

	pcwlnode = db.pcwlnode_test.find_one({"floor":floor,"pcwl_id":node})
	adjacent_nodes.extend(pcwlnode["next_id"])
	if len(adjacent_nodes) >= 3:
		return adjacent_nodes
	elif adjacent_flag:
		return adjacent_nodes
	else:
		return [node]




def find_ideal_nodes(floor,dlist,delta_distance):
	tmp_distance = 0 # 一次保存用
	next_distance = 0 # 計算した場所から次ノードまでの距離
	prev_distance = 0 # 計算した場所から前ノードまでの距離
	for i in range(len(dlist)):
		tmp_distance += dlist[i]["distance"]
		if tmp_distance >= delta_distance:
			next_distance = tmp_distance - delta_distance
			prev_distance = dlist[i]["distance"] - next_distance
			if next_distance < MATCH_NODE_THRESHOLD:
				return find_adjacent_nodes(floor,dlist[i]["direction"][1],ADJACENT_FLAG)
			elif prev_distance < MATCH_NODE_THRESHOLD:
				return find_adjacent_nodes(floor,dlist[i]["direction"][0],ADJACENT_FLAG)
			else:
				return dlist[i]["direction"]
	return find_adjacent_nodes(floor,dlist[i]["direction"][1],ADJACENT_FLAG)

# judge correct, judge data exists, and insert examine_route  
def judge_and_ins_correct_route(mac,floor,nodes,st_dt,st_next05_dt,examine_count,correct_count,exist_count):
	# is_correct = is_correct_node(mac,floor,st_next05_dt,nodes)
	is_correct, analyzed_data = is_correct_node(mac,floor,st_next05_dt,nodes)
	is_exist = is_exist_data(mac,floor,st_next05_dt,nodes)
	examine_count += 1
	if is_correct:
		correct_count += 1
	if is_exist:
		exist_count += 1
	db.examine_route.insert({"datetime":st_next05_dt,"nodes":nodes,"is_correct":is_correct})
	if DEBUG_PRINT:
		print(str(st_next05_dt) + " : " + str(nodes) + " , " + str(is_correct)+ " , "+ str(analyzed_data))
	# print("    analyzed data     " + str(analyzed_data))
	return examine_count, correct_count, exist_count


def generate_ideal_nodes(mac,floor,st_node,ed_node,st_dt,ed_dt):
	
	ideal_one_route = {}
	total_distance = 0
	delta_distance = 0
	velocity = 0
	nodes = []
	tmp_dlist = []
	dlist = []
	data = {}
	is_correct = False
	is_exist = False
	correct_count = 0
	examine_count = 0
	exist_count   = 0
	# [正解数,判定数]

	if st_node == ed_node:
		nodes = find_adjacent_nodes(floor,st_node,ADJACENT_FLAG)

		if db.examine_route.find({"datetime":st_dt}).count() == 0:
			nodes = find_adjacent_nodes(floor,st_node,ADJACENT_FLAG)
			st_next05_dt = dt_to_end_next05(st_dt,"iso")
			examine_count, correct_count, exist_count = judge_and_ins_correct_route(mac,floor,nodes,st_dt,st_next05_dt,examine_count,correct_count,exist_count)

		else:
			st_next05_dt = st_dt

		while st_next05_dt <= shift_seconds(ed_dt,-UPDATE_INTERVAL):
			st_next05_dt = shift_seconds(st_next05_dt,UPDATE_INTERVAL)
			examine_count, correct_count, exist_count = judge_and_ins_correct_route(mac,floor,nodes,st_dt,st_next05_dt,examine_count,correct_count,exist_count)
		return [correct_count,examine_count,exist_count]




	ideal_one_route = db.idealroute.find_one({"$and": [{"floor" : floor},{"query" : st_node},{"query" : ed_node}]})

	if ideal_one_route["query"][0] != st_node:
		tmp_dlist = ideal_one_route["dlist"]
		for i in range(-1,-len(tmp_dlist)-1,-1):
			dlist.append({"direction":[tmp_dlist[i]["direction"][1],tmp_dlist[i]["direction"][0]],"distance":tmp_dlist[i]["distance"]})
	else:
		dlist =  ideal_one_route["dlist"]
	total_distance = ideal_one_route["total_distance"]
	velocity = total_distance / (ed_dt - st_dt).seconds
	if DEBUG_PRINT:
		print("\n" + "from " + str(st_node) + " to " + str(ed_node) + " : velocity = " + str(rounding(velocity,2)) + " [px/s]")
	# tmp_distance = dlist[0]["distance"]
	if db.examine_route.find({"datetime":st_dt}).count() == 0:
		st_next05_dt = dt_to_end_next05(st_dt,"iso")
		delta_distance = velocity * (st_next05_dt - st_dt).seconds
		nodes = find_ideal_nodes(floor,dlist,delta_distance)
		examine_count, correct_count, exist_count = judge_and_ins_correct_route(mac,floor,nodes,st_dt,st_next05_dt,examine_count,correct_count,exist_count)
	else:
		st_next05_dt = st_dt

	while st_next05_dt <= shift_seconds(ed_dt,-UPDATE_INTERVAL):
		delta_distance += velocity * UPDATE_INTERVAL
		nodes = find_ideal_nodes(floor,dlist,delta_distance)
		st_next05_dt = shift_seconds(st_next05_dt,UPDATE_INTERVAL)
		examine_count, correct_count, exist_count = judge_and_ins_correct_route(mac,floor,nodes,st_dt,st_next05_dt,examine_count,correct_count,exist_count)

	return [correct_count,examine_count,exist_count]

def update_count(results,total_correct_count,total_examine_count,total_exist_count):
	total_correct_count += results[0]
	total_examine_count += results[1]
	total_exist_count   += results[2]
	return [total_correct_count, total_examine_count, total_exist_count]

def print_count_result(updated_list):
	total_correct_count, total_examine_count,total_exist_count = updated_list

	if total_examine_count == 0 :
		print("--- no data!! ---")
	else:
		correct_answer_rate = total_correct_count / total_examine_count * 100
		correct_answer_rate = rounding(correct_answer_rate, 2)
		print ("\n" + "correct answer rate : " + str(correct_answer_rate) + "% "
		 + "( " + str(total_correct_count) + " / " + str(total_examine_count) + " )")


	if total_exist_count == 0 :
		print("--- info_data does not exist! ---")
	else:
		correct_answer_rate_alt = total_correct_count / total_exist_count * 100
		correct_answer_rate_alt = rounding(correct_answer_rate_alt, 2)
		print ("accuracy[exist only]: " + str(correct_answer_rate_alt) + "% "
		 + "( " + str(total_correct_count) + " / " + str(total_exist_count) + " )")
	
def examine_route(mac,floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list):
	result = []
	total_correct_count = 0
	total_examine_count = 0
	total_exist_count   = 0
	correct_answer_rate = 0
	correct_answer_rate_alt = 0

	via_num = len(via_nodes_list)
	if via_num == 0:
		results = generate_ideal_nodes(mac,floor,st_node,ed_node,st_dt,ed_dt)
		updated = update_count(results,total_correct_count,total_examine_count,total_exist_count)
		total_correct_count, total_examine_count, total_exist_count = updated
		print_count_result(updated)

	else:
		#print(st_dt,via_dts_list[0])
		results = generate_ideal_nodes(mac,floor,st_node,via_nodes_list[0],st_dt,via_dts_list[0])
		updated = update_count(results,total_correct_count,total_examine_count,total_exist_count)
		total_correct_count, total_examine_count, total_exist_count = updated

		for i in range(via_num - 1):
			results = generate_ideal_nodes(mac,floor,via_nodes_list[i],via_nodes_list[i+1],via_dts_list[i],via_dts_list[i+1])
			updated = update_count(results,total_correct_count,total_examine_count,total_exist_count)
			total_correct_count, total_examine_count, total_exist_count = updated

		results = generate_ideal_nodes(mac,floor,via_nodes_list[-1],ed_node,via_dts_list[-1],ed_dt)
		updated = update_count(results,total_correct_count,total_examine_count,total_exist_count)
		total_correct_count, total_examine_count, total_exist_count = updated
		print_count_result(updated)



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
	# st_node = 5
	# ed_node = 5
	# via_nodes_list = []
	# common_dt = str(20161020) # 測定時刻における先頭の共通部分
	# st_dt = dt_from_14digits_to_iso(common_dt + str(115600))
	# ed_dt = dt_from_14digits_to_iso(common_dt + str(120920))
	# via_dts_list = []


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

	for i in range(len(via_dts_list)):
		via_dts_list[i] = dt_from_14digits_to_iso(common_dt + str(via_dts_list[i]))
	examine_route(mac,floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list)

# debug用
# py examine_route.py "W2-6F" [1,16] [5,8] 2016102510 [2609,2812] [2641,2730]




