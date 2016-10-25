# -*- coding: utf-8 -*-
# import sys
# sys.stdout = open("tmep.txt","w")
import datetime
from math import sqrt
from pymongo import *
client = MongoClient()
db = client.nm4bd

# DB初期化
db.pcwlroute_test.remove()
db.idealroute.remove()

# CONST
FLOOR_LIST = ["W2-6F","W2-7F","W2-8F","W2-9F","kaiyo"]
DISTANCE_THRESHOULD = 1.5 # 最短から1.5倍までの距離は許容




# 経路を探索する際に再帰的に用いる関数
def search_route(floor_nodes,register_order,route_list,ed_id):
	result = []
	for n in floor_nodes[register_order[route_list[-1]]]["next_id"]:
		if n not in route_list: # 一度通った道は再度通らない制約
			if n == ed_id:
				# print("route_list = "+str(route_list+[n]))
				result.append(route_list+[n])
			else :
				search_route(floor_nodes,register_order,route_list+[n],ed_id)
	return result

def find_ideal_route(floor_nodes,register_order,all_route_list):
	min_d = 99999999
	result = []
	st = 0
	ed = 0
	distance = 0

	for route_list in all_route_list:
		print("a")
		total_d = 0
		direction_list = [] # 一時的に経路と距離を記録
		for i in range(0,len(route_list)-1):
			st = register_order[route_list[i]]
			ed = register_order[route_list[i+1]]
			distance = sqrt(pow(floor_nodes[st]["pos_x"]-floor_nodes[ed]["pos_x"],2)+pow(floor_nodes[st]["pos_y"]-floor_nodes[ed]["pos_y"],2))
			print(distance)
			total_d += distance
			direction_list.append({"distance":distance,"direction":[route_list[i],route_list[i+1]]})
			print(total_d)
	
		if total_d < min_d:
			print("a")
			result = direction_list
			min_d = total_d

	return {"dlist":result,"total_distance":min_d}

def distance_filtering(floor_nodes,register_order,all_route_list,distance_threshould):
	min_d = 99999999
	result = []
	st = 0
	ed = 0
	distance = 0

	for route_list in all_route_list:
		total_d = 0
		direction_list = [] # 一時的に経路と距離を記録
		for i in range(0,len(route_list)-1):
			st = register_order[route_list[i]]
			ed = register_order[route_list[i+1]]
			distance = sqrt(pow(floor_nodes[st]["pos_x"]-floor_nodes[ed]["pos_x"],2)+pow(floor_nodes[st]["pos_y"]-floor_nodes[ed]["pos_y"],2))
			total_d += distance
			direction_list.append({"distance":distance,"direction":[route_list[i],route_list[i+1]]})
		
			if total_d < min_d:
				directions = direction_list
				min_d = total_d

		if total_d < min_d * distance_threshould: # 合計距離がしきい値の条件を満たす時、以下を実行
			if total_d * distance_threshould < min_d: #　最新 < 以前 * 1/(しきい値)倍の時（最短）
				result = [direction_list] # 以前の記録は消去してよく、新たにresultを作成
				min_d = total_d # 最小距離を更新
			elif total_d < min_d : # 以前 * 1/(しきい値)倍 < 最新 < 以前の記録の時
				result.insert(0,direction_list) # 先頭に挿入
				min_d = total_d
			else :
				result.append(direction_list)
	return result

def make_pcwlroute():
	# 変数定義
	floor_nodes = []
	register_order = []
	st_id = 0
	ed_id = 0
	next_distance = 0
	all_route_list = []
	dlist = []
	ddict = {}
	for floor in FLOOR_LIST:
		floor_nodes = [] # nodes in the certain floor
		floor_nodes += db.pcwlnode_test.find({"floor":floor})

		# pcwl_idからfloor_nodesでのインデックスを求められるように
		# (register_order[pcwl_id] = floor_nodesでのインデックス)
		register_order = [0]*99
		for i in range(0,len(floor_nodes)):
			register_order[floor_nodes[i]["pcwl_id"]] = i
		print(register_order)
		for i in range(0,len(floor_nodes)):
			for j in range(i+1,len(floor_nodes)):
				st_id = floor_nodes[i]["pcwl_id"] # 出発点のpcwl_id
				ed_id = floor_nodes[j]["pcwl_id"] # 到着点のpcwl_id

				# 出発点と到着点が隣接ならばそれらの間のルートを登録
				if ed_id in floor_nodes[i]["next_id"]:
					next_distance = sqrt(pow(floor_nodes[i]["pos_x"]-floor_nodes[j]["pos_x"],2)+pow(floor_nodes[i]["pos_y"]-floor_nodes[j]["pos_y"],2))
					db.pcwlroute_test.insert({"query":[st_id,ed_id],"dlist":[[{"direction":[st_id,ed_id],"distance":next_distance}]],"floor":floor})
					db.idealroute.insert({"query":[st_id,ed_id],"dlist":[{"direction":[st_id,ed_id],"distance":next_distance}],"total_distance":next_distance,"floor":floor})
				# 隣接ではない場合
				else :
					all_route_list = search_route(floor_nodes,register_order,[st_id],ed_id)
					dlist = distance_filtering(floor_nodes,register_order,all_route_list,DISTANCE_THRESHOULD)
					db.pcwlroute_test.insert({"query":[st_id,ed_id],"dlist":dlist,"floor":floor})

					ddict = find_ideal_route(floor_nodes,register_order,all_route_list)
					db.idealroute.insert({"query":[st_id,ed_id],"dlist":ddict["dlist"],"total_distance":ddict["total_distance"],"floor":floor})

# sys.stdout.close()

if __name__ == '__main__':
    make_pcwlroute()


