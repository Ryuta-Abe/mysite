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
MAC = "00:11:81:10:01:1c"

def is_correct_node(floor,dt,nodes):
	analyze_time = shift_seconds(dt,ANALYZE_LAG)
	analyze_data = {}
	for node in nodes:
		analyze_data = db.pfvmacinfo.find_one({"floor":floor,"datetime":analyze_time,"mac":MAC})
		if analyze_data is not None and analyze_data["route"][-1][1] == node:
			return True
		elif db.staymacinfo.find({"floor":floor,"datetime":analyze_time,"mac":MAC,"pcwl_id":node}).count() == 1:
			return True
	return False



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
	tmp_dlist = []
	dlist = []
	data = {}
	is_correct = False
	correct_count = 0
	examine_count = 0
	# [正解数,判定数]

	ideal_one_route = db.idealroute.find_one({"$and": [{"floor" : floor},{"query" : st_node},{"query" : ed_node}]})

	if ideal_one_route["query"][0] != st_node:
		tmp_dlist = ideal_one_route["dlist"]
		for i in range(-1,-len(tmp_dlist)-1,-1):
			dlist.append({"direction":[tmp_dlist[i]["direction"][1],tmp_dlist[i]["direction"][0]],"distance":tmp_dlist[i]["distance"]})
	else:
		dlist =  ideal_one_route["dlist"]
	total_distance = ideal_one_route["total_distance"]
	velocity = total_distance / (ed_dt - st_dt).seconds
	print("from " + str(st_node) + " to " + str(ed_node) + " : velocity = " + str(velocity))
	# tmp_distance = dlist[0]["distance"]
	if db.examine_route.find({"datetime":st_dt}).count() == 0:
		st_next05_dt = dt_to_end_next05(st_dt,"iso")
		delta_distance = velocity * (st_next05_dt - st_dt).seconds
		nodes = find_closest_nodes(dlist,delta_distance)
		
		is_correct = is_correct_node(floor,st_next05_dt,nodes)
		examine_count += 1
		if is_correct:
			correct_count += 1
		
		db.examine_route.insert({"datetime":st_next05_dt,"nodes":nodes,"is_correct":is_correct})
		print(str(st_next05_dt) + " : " + str(nodes) + " , " + str(is_correct))
	else:
		st_next05_dt = st_dt

	while st_next05_dt <= shift_seconds(ed_dt,-UPDATE_INTERVAL):
		delta_distance += velocity * UPDATE_INTERVAL
		nodes = find_closest_nodes(dlist,delta_distance)
		st_next05_dt = shift_seconds(st_next05_dt,UPDATE_INTERVAL)

		is_correct = is_correct_node(floor,st_next05_dt,nodes)
		examine_count += 1
		if is_correct:
			correct_count += 1
		
		db.examine_route.insert({"datetime":st_next05_dt,"nodes":nodes,"is_correct":is_correct})
		print(str(st_next05_dt) + " : " + str(nodes) + " , " + str(is_correct))
	print("\n")
	return [correct_count,examine_count]

	
def examine_route(floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list):
	result = []
	total_correct_count = 0
	total_examine_count = 0
	correct_answer_rate = 0

	via_num = len(via_nodes_list)
	if via_num == 0:
		result = generate_ideal_nodes(floor,st_node,ed_node,st_dt,ed_dt)
		total_correct_count = result[0]
		total_examine_count = result[1]
		correct_answer_rate = total_correct_count / total_examine_count * 100
		print ("correct answer rate : " + str(correct_answer_rate) + "% "
		 + "( " + str(total_correct_count) + " / " + str(total_examine_count) + " )")

	else:
		#print(st_dt,via_dts_list[0])
		result = generate_ideal_nodes(floor,st_node,via_nodes_list[0],st_dt,via_dts_list[0])
		total_correct_count = result[0]
		total_examine_count = result[1]
		for i in range(via_num - 1):
			result = generate_ideal_nodes(floor,via_nodes_list[i],via_nodes_list[i+1],via_dts_list[i],via_dts_list[i+1])
			total_correct_count += result[0]
			total_examine_count += result[1]
		result = generate_ideal_nodes(floor,via_nodes_list[-1],ed_node,via_dts_list[-1],ed_dt)
		total_correct_count += result[0]
		total_examine_count += result[1]
		correct_answer_rate = total_correct_count / total_examine_count * 100
		print ("correct answer rate : " + str(correct_answer_rate) + "% "
		 + "( " + str(total_correct_count) + " / " + str(total_examine_count) + " )")
	# examine_route += db.examine_route.find()
	# for nodes_info in examine_route:
	# 	if db.pfvmacinfo.find()




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
	floor = "W2-7F"
	st_node = 1
	ed_node = 1
	via_nodes_list = [5,7,9,12,17,21,5]
	common_dt = str(20161020) # 測定時刻における先頭の共通部分
	st_dt = dt_from_14digits_to_iso(common_dt + str(125800))
	ed_dt = dt_from_14digits_to_iso(common_dt + str(130126))
	via_dts_list = [125827,125854,125925,125942,130010,130041,130058]
	for i in range(len(via_dts_list)):
		via_dts_list[i] = dt_from_14digits_to_iso(common_dt + str(via_dts_list[i]))
	examine_route(floor,st_node,ed_node,via_nodes_list,st_dt,ed_dt,via_dts_list)

# debug用
# py examine_route.py "W2-6F" [1,16] [5,8] 2016102510 [2609,2812] [2641,2730]




