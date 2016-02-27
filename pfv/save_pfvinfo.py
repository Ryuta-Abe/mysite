# -*- coding: utf-8 -*-
import datetime
import math

# mongoDBに接続
from mongoengine import *
from pymongo import *

from pfv.models import pcwlnode, pfvinfo, pfvmacinfo, pfvinfoexperiment, pfvinfoexperiment2, pcwlroute, pcwltime, stayinfo, staymacinfo

client = MongoClient()
db = client.nm4bd
db.pcwltime.create_index([("datetime", ASCENDING)])
db.pfvinfo.create_index([("datetime", ASCENDING)])
db.stayinfo.create_index([("datetime", ASCENDING)])
db.pcwlroute.create_index([("query", ASCENDING)])

# ここからコメントアウト(ローカルテスト時に使うんで残しといて)
# connect('nm4bd')

# # PCWLのノード情報
# class pcwlnode(Document):
#     pcwl_id = IntField()
#     pos_x = IntField()
#     pos_y = IntField()
#     next_id = ListField(IntField())

# # PCWLの経路情報
# class pcwlroute(Document):
#     query = ListField(IntField())
#     dlist = ListField(ListField(DictField()))

# # 人流情報
# class pfvinfo(Document):
#     plist = ListField(DictField())
#     datetime = DateTimeField()

# # 人流情報(6F実験用)
# class pfvinfoexperiment(Document):
#     plist = ListField(DictField())
#     datetime = DateTimeField()

# # 残留端末情報
# class stayinfo(Document):
#     plist = ListField(DictField())
#     datetime = DateTimeField()

# class pcwltime(Document):
#     _id = StringField()
#     datetime = DateTimeField()

# # 人流情報(mac情報付き)
# class pfvmacinfo(Document):
#     datetime = DateTimeField()
#     mac = StringField()
#     plist = ListField(DictField())
#     floor = StringField()

#     meta = {
#         "db_alias" : "nm4bd",
#     }

# ここまでコメントアウト

floor_list = ["W2-6F","W2-7F","kaiyo"]
pfvinfo_dict  = {}
stayinfo_dict = {}

_pcwlnode = {}

for floor in floor_list:
	# PCWLノード情報取り出し
	# _pcwlnode += pcwlnode.objects()
	node_list = []
	node_list += db.pcwlnode.find({"floor":floor})
	_pcwlnode.update({floor:node_list})
	# _pcwlnode += db.pcwlnode.find({"floor":floor})

	# st,edからpfvinfoの登録順を求める(例：pfvinfo_id[3][4] = 4)
	pfvinfo_id = []
	for i in range(0,99):
		pfvinfo_id.append([0]*99)
	count = 0
	for i in range(0,len(_pcwlnode[floor])):
		for j in range(0,len(_pcwlnode[floor])):
			st = _pcwlnode[floor][i]["pcwl_id"] # 出発点
			ed = _pcwlnode[floor][j]["pcwl_id"] # 到着点
			if ed in _pcwlnode[floor][i]["next_id"]:
				pfvinfo_id[st][ed] = count
				count += 1
	pfvinfo_dict.update({floor:pfvinfo_id})

	# idからstayinfoの登録順を求める
	stayinfo_id = [0]*99
	for i in range(0,len(_pcwlnode[floor])):
		stayinfo_id[_pcwlnode[floor][i]["pcwl_id"]] = i
		stayinfo_dict.update({floor:stayinfo_id})

# pfvinfo関係
def make_empty_pfvinfo(dt,db_name,floor): # 空のpfvinfoを作成
	# print(str(dt)+"の空のpfvinfoを作成")
	plist = []
	# ノード同士の全組み合わせで経路情報を記録
	for i in range(0,len(_pcwlnode[floor])):
		for j in range(0,len(_pcwlnode[floor])):
			st = _pcwlnode[floor][i]["pcwl_id"] # 出発点
			ed = _pcwlnode[floor][j]["pcwl_id"] # 到着点
			# iとjが隣接ならば人流0人でplistに加える
			if ed in _pcwlnode[floor][i]["next_id"]:
				if is_experiment(db_name):
					plist.append({"direction":[st,ed],"size":0,"mac_list":[]})
				else :
					plist.append({"direction":[st,ed],"size":0})
	return {'datetime':dt,'plist':plist, "floor":floor}

def optimize_routeinfo(st_list,ed_list,route_info): # 向きの最適化と各経路の重みを計算
	output = []

	# 経路情報の向きを最適化(st > edの場合にリストとdirectionの中身を逆向きに)
	if st_list[0]["pcwl_id"] > ed_list[0]["pcwl_id"]:
		for route in route_info:
			reverse = []
			for i in range(-1,-len(route)-1,-1):
				reverse.append({"direction":[route[i]["direction"][1],route[i]["direction"][0]],
					"distance":route[i]["distance"]})
			output.append({"route":reverse})
	else :
		for route in route_info:
			output.append({"route":route})

	# 各経路の重みを計算
	if len(route_info) > 1: # 経路が複数の場合

		# 距離による重み付け
		d_total = 0 #全経路の総距離
		for route in output:
			d_route = 0 #一つの経路の距離
			for node in route["route"]:
				d_route += node["distance"]
			route["distance"] = d_route
			d_total += d_route
		add_total = 0 # 各addの合計値を1にするため用いる
		for route in output:
			tmp_add = (d_total - route["distance"]) / d_total / (len(output) - 1)
			add_total += tmp_add * tmp_add
		for route in output:
			tmp_add = (d_total - route["distance"]) / d_total / (len(route_info) - 1)
			route["add"] = tmp_add * tmp_add / add_total

		# # 2番目以降に強いRSSIによる重み付け
		# for route in output:
		# 	route["add"] = 0
		# 	num_list = [] # 出発点、到着点を除いたrouteに含まれるnode番号の数字列
		# 	for i in range(1,len(route["route"])):
		# 		num_list.append(route["route"][i]["direction"][0])
		# 	for i in range(1,len(st)):
		# 		if st[i] in num_list:
		# 			route["add"] += 1/i
		# 	for i in range(1,len(ed)):
		# 		if ed[i] in num_list:
		# 			route["add"] += 1/i
		# add_total = 0 # 各addの合計値を1にするため用いる
		# for route in output:
		# 	add_total += route["add"]
		# if add_total != 0:
		# 	for route in output:
		# 		route["add"] /= add_total
		# else : # 2番目以降に強いRSSIがどの経路においても一つも一致しなかった場合
		# 	for route in output:
		# 		route["add"] = 1/len(output)

	else : # 経路が1つの場合
		output[0]["add"] = 1
		d_route = 0 #一つの経路の距離
		for node in output[0]["route"]:
			d_route += node["distance"]
		output[0]["distance"] = d_route

	return output

def select_one_route(route_info): # 入力：複数の経路、出力：最もaddが大きい経路1つ
	add_max = 0
	for route in route_info:
		if add_max < route["add"]:
			add_max = route["add"]
			output = route
	return [output]

def make_pfvinfo(dataset,db_name,all_flag):
	# 開始時にDBを初期化
	if all_flag:
		db_name.remove()
	
	progress = 0
	for data in dataset:
		interval = round(data["interval"])
		num = int(round(interval / 10)) # 40秒間隔の場合, num = 4
		tlist = db.pcwltime.find({"datetime":{"$gt":data["start_time"]}}).sort("datetime", ASCENDING).limit(num)
		route_info = [] # 経路情報の取り出し
		route_info += db.pcwlroute.find({"$and": [
													{"floor" : data["floor"]},
													{"query" : data["start_node"][0]["pcwl_id"]}, 
													{"query" : data["end_node"][0]["pcwl_id"]}
												]})
		route_info = optimize_routeinfo(data["start_node"],data["end_node"],route_info[0]["dlist"]) # 向きの最適化と各経路の重み付けを行う
		# print("[出発点,到着点] = "+str([data["start_node"][0]["pcwl_id"], data["end_node"][0]["pcwl_id"]])+" , 間隔 = "+str(interval)+" 秒 floor:"+data["floor"])

		if num >= 1:
			for route in route_info: # ある経路に対して以下を実行
				# print("add = "+str(route["add"]))

				# 抜けている出発到着情報の補完
				if num > 1:
					total_distance = route["distance"]
					tmp_distance = 0 # 推定に用いる一時累計距離
					st_ed_info = [] # 欠落した出発到着情報を補完するリスト
					tmp_st_ed_info = []
					n_count = 0 # ノード情報のカウンター
					t_count = 1 # タイム情報のカウンター
					while t_count < num:
						tmp_distance += route["route"][n_count]["distance"]
						tmp_st_ed_info.append(route["route"][n_count]["direction"])
						if tmp_distance >= (total_distance*t_count/num): # 一時累計距離がしきい値を超えたら以下を実行
							extra_distance = tmp_distance - (total_distance*t_count/num)
							if extra_distance >= (route["route"][n_count]["distance"]/2):
								tmp_st_ed_info.pop(-1)
								tmp_distance -= route["route"][n_count]["distance"]
							else :
								n_count += 1
							st_ed_info.append(tmp_st_ed_info)
							tmp_st_ed_info = []
							t_count += 1
							if n_count == len(route["route"]):
								for i in range(t_count-1,num):
									st_ed_info.append([])
								break
							if t_count == num:
								for i in range(n_count,len(route["route"])):
									tmp_st_ed_info.append(route["route"][i]["direction"])
								st_ed_info.append(tmp_st_ed_info)
						else :
							n_count += 1
				elif num == 1:
					tmp_st_ed_info = []
					for node in route["route"]:
						tmp_st_ed_info.append(node["direction"])
					st_ed_info = [tmp_st_ed_info]
				# print("st_ed_info = "+str(st_ed_info))

				# pfv情報の登録
				# print("interval : "+str(interval))
				for j in range(0,num):
					if len(st_ed_info[j]) >= 1: # j番目の時刻において出発点到着点が同じ場合は以下をスキップ
						tmp_plist = db_name.find_one({"datetime":{"$eq":tlist[j]["datetime"]},"floor":data["floor"]})
						if tmp_plist == None: # この時間の情報がまだDBに登録されていない場合
							tmp_plist = make_empty_pfvinfo(tlist[j]["datetime"], db_name, data["floor"]) # この時間の空の情報を作成
						for dire in st_ed_info[j]:
							tmp_plist["plist"][pfvinfo_dict[data["floor"]][dire[0]][dire[1]]]["size"] += route["add"]
							if is_experiment(db_name):
								if data["mac"] not in tmp_plist["plist"][pfvinfo_dict[data["floor"]][dire[0]][dire[1]]]["mac_list"]:
									tmp_plist["plist"][pfvinfo_dict[data["floor"]][dire[0]][dire[1]]]["mac_list"] += [data["mac"]]
						db_name.save(tmp_plist)
						# print(str(tlist[j]["datetime"])+"のpfvinfoを登録完了, 経路分岐 = "+str(len(route_info))+" floor:"+data["floor"])

		progress += 1
		if ((progress % 1000) == 0) or (progress == len(dataset)):
			print("pfvinfo "+str(progress)+" / "+str(len(dataset))+" ("+str(round(progress/len(dataset)*100,1))+"%)")
		# db_name.create_index([("datetime", ASCENDING)])

def is_experiment(db_name): # 実験用DBか否かを判定
	if (db_name == db.pfvinfoexperiment) or (db_name == db.pfvinfoexperiment2):
		return True
	else :
		return False

# mac情報付きpfvinfo
def make_pfvmacinfo(dataset,db_name,all_flag):
	# 開始時にDBを初期化
	if all_flag:
		db_name.remove()
		db.staymacinfo.remove()

	progress = 0
	for data in dataset:
		interval = round(data["interval"])
		num = int(round(interval / 10)) # 40秒間隔の場合, num = 4
		tlist = db.pcwltime.find({"datetime":{"$gt":data["start_time"]}}).sort("datetime", ASCENDING).limit(num)
		route_info = [] # 経路情報の取り出し
		route_info += db.pcwlroute.find({"$and": [
													{"floor" : data["floor"]},
													{"query" : data["start_node"][0]["pcwl_id"]}, 
													{"query" : data["end_node"][0]["pcwl_id"]}
												]
												# ,"floor":data["floor"]
												})
		route_info = optimize_routeinfo(data["start_node"],data["end_node"],route_info[0]["dlist"]) # 向きの最適化と各経路の重み付けを行う
		if len(route_info) >= 2:
			route_info = select_one_route(route_info) # addが最大の1つの経路のみ取り出す

		if num >= 1:
			for route in route_info: # ある経路に対して以下を実行

				# 抜けている出発到着情報の補完
				if num > 1:
					total_distance = route["distance"]
					tmp_distance = 0 # 推定に用いる一時累計距離
					st_ed_info = [] # 欠落した出発到着情報を補完するリスト
					tmp_st_ed_info = []
					n_count = 0 # ノード情報のカウンター
					t_count = 1 # タイム情報のカウンター
					while t_count < num:
						tmp_distance += route["route"][n_count]["distance"]
						tmp_st_ed_info.append(route["route"][n_count]["direction"])
						if tmp_distance >= (total_distance*t_count/num): # 一時累計距離がしきい値を超えたら以下を実行
							extra_distance = tmp_distance - (total_distance*t_count/num)
							if extra_distance >= (route["route"][n_count]["distance"]/2):
								tmp_st_ed_info.pop(-1)
								tmp_distance -= route["route"][n_count]["distance"]
							else :
								n_count += 1
							st_ed_info.append(tmp_st_ed_info)
							tmp_st_ed_info = []
							t_count += 1
							if n_count == len(route["route"]):
								for i in range(t_count-1,num):
									st_ed_info.append([])
								break
							if t_count == num:
								for i in range(n_count,len(route["route"])):
									tmp_st_ed_info.append(route["route"][i]["direction"])
								st_ed_info.append(tmp_st_ed_info)
						else :
							n_count += 1
				elif num == 1:
					tmp_st_ed_info = []
					for node in route["route"]:
						tmp_st_ed_info.append(node["direction"])
					st_ed_info = [tmp_st_ed_info]

				# 人流情報or滞留情報の登録
				location = data["start_node"][0]["pcwl_id"] # 現在位置の情報
				for j in range(0,num):
					if len(st_ed_info[j]) >= 1: # j番目の時刻において出発点到着点が異なる場合は人流情報を記録
						new_data = {"datetime":tlist[j]["datetime"],"mac":data["mac"],"route":st_ed_info[j],"floor":data["floor"]}
						db_name.insert(new_data)
						location = st_ed_info[j][-1][-1]
					else: # j番目の時刻において出発点到着点が同じ場合は滞留情報を記録
						new_data = {"datetime":tlist[j]["datetime"],"mac":data["mac"],"pcwl_id":location,"floor":data["floor"]}
						db.staymacinfo.insert(new_data)

		progress += 1
		if ((progress % 1000) == 0) or (progress == len(dataset)):
			print("pfvmacinfo "+str(progress)+" / "+str(len(dataset))+" ("+str(round(progress/len(dataset)*100,1))+"%)")
		# db_name.create_index([("datetime", ASCENDING)])

# 滞留端末情報stayinfo関係
def make_empty_stayinfo(dt,floor): # 空のstayinfoを作成
	# print(str(dt)+"の空のstayinfoを作成")
	plist = []
	for node in _pcwlnode[floor]:
		plist.append({"pcwl_id":node["pcwl_id"],"size":0,"mac_list":[]})
	return {'datetime':dt,'plist':plist,'floor':floor}

def make_stayinfo(dataset,db_name,all_flag):
	# stayinfoを初期化
	if all_flag:
		db_name.remove()

	progress = 0
	for data in dataset:
		interval = round(data["interval"])
		num = int(round(interval / 10)) # 40秒間隔の場合, num = 4
		tlist = db.pcwltime.find({"datetime":{"$gt":data["start_time"]}}).sort("datetime", ASCENDING).limit(num)

		# print("interval : "+str(interval))
		for i in range(0,num):

			# 滞留端末情報の一時データ取り出し
			tmp_plist = db_name.find_one({"datetime":{"$eq":tlist[i]["datetime"]},"floor":data["floor"]})
			if tmp_plist == None: # この時間の情報がまだDBに登録されていない場合
				tmp_plist = make_empty_stayinfo(tlist[i]["datetime"],data["floor"]) # この時間の空の情報を作成

				# 滞留端末情報更新
			tmp_plist["plist"][stayinfo_dict[data["floor"]][data["start_node"]]]["size"] += 1
			tmp_plist["plist"][stayinfo_dict[data["floor"]][data["start_node"]]]["mac_list"] += [data["mac"]]
			db_name.save(tmp_plist)
		# print(str(data["start_time"])+" interval = "+str(interval)+" node = "+str(data["start_node"])+" 保存")
		if ((progress % 1000) == 0) or (progress == len(dataset)):
			print("stayinfo "+str(progress)+" / "+str(len(dataset))+" ("+str(round(progress/len(dataset)*100,1))+"%)")
			# print(data["start_time"])
		progress += 1
		# db_name.create_index([("datetime", ASCENDING)])

def make_staymacinfo(dataset,db_name,all_flag):
	if all_flag:
		db_name.remove()

	progress = 0
	for data in dataset:
		interval = round(data["interval"])
		num = int(round(interval / 10)) # 40秒間隔の場合, num = 4
		# print("interval : "+str(interval))
		tlist = db.pcwltime.find({"datetime":{"$gt":data["start_time"]}}).sort("datetime", ASCENDING).limit(num)

		for i in range(0,num):
			
			# 滞留端末情報更新
			new_data = {"datetime":tlist[i]["datetime"],"mac":data["mac"],"pcwl_id":data["start_node"],"floor":data["floor"]}
			db_name.insert(new_data)

		progress += 1
		if ((progress % 1000) == 0) or (progress == len(dataset)):
			print("staymacinfo "+str(progress)+" / "+str(len(dataset))+" ("+str(round(progress/len(dataset)*100,1))+"%)")
		# db_name.create_index([("datetime", ASCENDING)])
		
# # 出発時刻、出発点、到着時刻、到着点のデータセット
# dataset = []
# dataset.append({"mac":"a","start_node":[{"pcwl_id":1,"rssi":-60},{"pcwl_id":21,"rssi":-65},{"pcwl_id":27,"rssi":-70}],"start_time":datetime.datetime(2015,6,3,12,10,4),"end_node":[{"pcwl_id":11,"rssi":-60},{"pcwl_id":12,"rssi":-65}],"end_time":datetime.datetime(2015,6,3,12,10,54),"interval":50})
# dataset.append({"mac":"b","start_node":[{"pcwl_id":5,"rssi":-60}],"start_time":datetime.datetime(2015,6,3,12,10,24),"end_node":[{"pcwl_id":9,"rssi":-60}],"end_time":datetime.datetime(2015,6,3,12,10,54),"interval":30})
# dataset.append({"mac":"c","start_node":[{"pcwl_id":13,"rssi":-60}],"start_time":datetime.datetime(2015,6,3,12,10,54),"end_node":[{"pcwl_id":9,"rssi":-60}],"end_time":datetime.datetime(2015,6,3,12,11,4),"interval":10})
# dataset.append({"mac":"d","start_node":[{"pcwl_id":1,"rssi":-60}],"start_time":datetime.datetime(2015,6,3,12,11,4),"end_node":[{"pcwl_id":5,"rssi":-60}],"end_time":datetime.datetime(2015,6,3,12,11,14),"interval":10})
# dataset.append({"mac":"e","start_node":[{"pcwl_id":1,"rssi":-60}],"start_time":datetime.datetime(2015,6,3,12,10,14),"end_node":[{"pcwl_id":5,"rssi":-60}],"end_time":datetime.datetime(2015,6,3,12,10,44),"interval":30})
# dataset.append({"mac":"f","start_node":[{"pcwl_id":9,"rssi":-60}],"start_time":datetime.datetime(2015,6,3,12,11,14),"end_node":[{"pcwl_id":13,"rssi":-60}],"end_time":datetime.datetime(2015,6,3,12,11,34),"interval":20})

# import time
# start = time.time()
# make_pfvmacinfo(dataset,db.pfvmacinfo)
# end = time.time()
# print("time:"+str(end-start))

# print("エラー無しやな")