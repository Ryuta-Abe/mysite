# -*- coding: utf-8 -*-
# import sys
# sys.stdout = open("tmep.txt","w")
import datetime
from math import sqrt
from pymongo import *
client = MongoClient()
db = client.nm4bd

# DB初期化
db.pcwlroute.remove()
db.idealroute.remove()

# CONST
FLOOR_LIST = ["W2-6F","W2-7F","W2-8F","W2-9F","kaiyo"]
DISTANCE_THRESHOULD = 1.5 # 最短から1.5倍までの距離は許容




# 経路を探索する際に再帰的に用いる関数
# 初回実行時はroute_list,all_route_listはそれぞれst_id,[]を入力
def search_route(floor_nodes,route_list,ed_id,all_route_list):
	for n in floor_nodes[route_list[-1]]["next_id"]:
		if n not in route_list: # 一度通った道は再度通らない制約
			if n == ed_id:
				# print("route_list = "+str(route_list+[n]))
				all_route_list.append(route_list+[n])
			else :
				search_route(floor_nodes,route_list+[n],ed_id,all_route_list)
	return all_route_list

def find_ideal_route(floor_nodes,all_route_list):
	min_d = 99999999
	direction_list = []
	result = []
	distance = 0
	

	for route_list in all_route_list:
		total_d = 0
		direction_list = [] # 一時的に経路と距離を記録
		for i in range(0,len(route_list)-1): # 隣接ノードごとに距離を算出し、合計距離を求める
			distance = sqrt(pow(floor_nodes[route_list[i]]["pos_x"]-floor_nodes[route_list[i+1]]["pos_x"],2)+pow(floor_nodes[route_list[i]]["pos_y"]-floor_nodes[route_list[i+1]]["pos_y"],2))
			total_d += distance
			direction_list.append({"distance":distance,"direction":[route_list[i],route_list[i+1]]})
	
		if total_d < min_d: # 最短のみ記録
			result = direction_list
			min_d = total_d

	return {"dlist":result,"total_distance":min_d}

def distance_filtering(floor_nodes,all_route_list,distance_threshould):
	min_d = 99999999
	direction_list = []
	result = []
	distance = 0
	
	for route_list in all_route_list:
		total_d = 0
		direction_list = [] # 一時的に経路と距離を記録
		for i in range(0,len(route_list)-1): # 隣接ノードごとに距離を算出し、合計距離を求める
			distance = sqrt(pow(floor_nodes[route_list[i]]["pos_x"]-floor_nodes[route_list[i+1]]["pos_x"],2)+pow(floor_nodes[route_list[i]]["pos_y"]-floor_nodes[route_list[i+1]]["pos_y"],2))
			total_d += distance
			direction_list.append({"distance":distance,"direction":[route_list[i],route_list[i+1]]})

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
	tmp_nodes = []
	floor_nodes = []
	st_id = 0
	ed_id = 0
	next_distance = 0
	all_route_list = []
	dlist = []
	ddict = {}
	for floor in FLOOR_LIST:
		tmp_nodes = [] 
		tmp_nodes += db.pcwlnode_test.find({"floor":floor})
		floor_nodes = [0]*99 # nodes in the certain floor
		for i in range(0,len(tmp_nodes)):
			floor_nodes[tmp_nodes[i]["pcwl_id"]] = tmp_nodes[i]
		# print(floor_nodes)

		# pcwl_idからfloor_nodesでのインデックスを求められるように
		# (register_order[pcwl_id] = floor_nodesでのインデックス)
		# register_order = [0]*99
		# for i in range(0,len(floor_nodes)):
		# 	register_order[floor_nodes[i]["pcwl_id"]] = i
		for i in range(0,len(floor_nodes)):
			for j in range(i+1,len(floor_nodes)):
				if floor_nodes[i] != 0 and floor_nodes[j] != 0 :
					st_id = floor_nodes[i]["pcwl_id"] # 出発点のpcwl_id
					ed_id = floor_nodes[j]["pcwl_id"] # 到着点のpcwl_id

					# 出発点と到着点が隣接ならばそれらの間のルートを登録
					if ed_id in floor_nodes[i]["next_id"]:
						next_distance = sqrt(pow(floor_nodes[i]["pos_x"]-floor_nodes[j]["pos_x"],2)+pow(floor_nodes[i]["pos_y"]-floor_nodes[j]["pos_y"],2))
						db.pcwlroute.insert({"query":[st_id,ed_id],"dlist":[[{"direction":[st_id,ed_id],"distance":next_distance}]],"floor":floor})
						db.idealroute.insert({"query":[st_id,ed_id],"dlist":[{"direction":[st_id,ed_id],"distance":next_distance}],"total_distance":next_distance,"floor":floor})
					# 隣接ではない場合
					else :
						all_route_list = search_route(floor_nodes,[st_id],ed_id,[])
						dlist = distance_filtering(floor_nodes,all_route_list,DISTANCE_THRESHOULD)
						db.pcwlroute.insert({"query":[st_id,ed_id],"dlist":dlist,"floor":floor})

						ddict = find_ideal_route(floor_nodes,all_route_list)
						db.idealroute.insert({"query":[st_id,ed_id],"dlist":ddict["dlist"],"total_distance":ddict["total_distance"],"floor":floor})

# sys.stdout.close()

if __name__ == '__main__':
    make_pcwlroute()


