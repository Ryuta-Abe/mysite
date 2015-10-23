import datetime
import math

# mongoDBに接続
from mongoengine import *
from pymongo import *

from pfv.models import pcwlnode, pfvinfo, pfvinfoexperiment, pcwlroute, pcwltime, stayinfo

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

# ここまでコメントアウト

# PCWLノード情報取り出し
_pcwlnode = []
# _pcwlnode += pcwlnode.objects()
_pcwlnode += db.pcwlnode.find()

# st,edからpfvinfoの登録順を求める(例：pfvinfo_id[3][4] = 4)
pfvinfo_id = []
for i in range(0,99):
	pfvinfo_id.append([0]*99)
count = 0
for i in range(0,len(_pcwlnode)):
	for j in range(0,len(_pcwlnode)):
		st = _pcwlnode[i]["pcwl_id"] # 出発点
		ed = _pcwlnode[j]["pcwl_id"] # 到着点
		if ed in _pcwlnode[i]["next_id"]:
			pfvinfo_id[st][ed] = count
			count += 1

# idからstayinfoの登録順を求める
stayinfo_id = [0]*99
for i in range(0,len(_pcwlnode)):
	stayinfo_id[_pcwlnode[i]["pcwl_id"]] = i

# pfvinfo関係
def make_empty_pfvinfo(dt): # 空のpfvinfoを作成
	# print(str(dt)+"の空のpfvinfoを作成")
	plist = []
	# ノード同士の全組み合わせで経路情報を記録
	for i in range(0,len(_pcwlnode)):
		for j in range(0,len(_pcwlnode)):
			st = _pcwlnode[i]["pcwl_id"] # 出発点
			ed = _pcwlnode[j]["pcwl_id"] # 到着点
			# iとjが隣接ならば人流0人でplistに加える
			if ed in _pcwlnode[i]["next_id"]:
				plist.append({"direction":[st,ed],"size":0})
	db.pfvinfo.insert({'datetime':dt,'plist':plist})

def optimize_direction(st,ed,route_info): # 経路情報の向きを最適化(st > edの場合にリストとdirectionの中身を逆向きに)
	if st < ed:
		return route_info
	else :
		output = []
		for route in route_info:
			reverse = []
			for i in range(-1,-len(route)-1,-1):
				reverse.append({"direction":[route[i]["direction"][1],route[i]["direction"][0]],
					"distance":route[i]["distance"]})
			output.append(reverse)
		return output

def make_pfvinfo(dataset):
	# 開始時にDBを初期化
	db.pfvinfo.remove()

	for data in dataset:
		interval = round(data["interval"])
		num = round(interval / 10) # 40秒間隔の場合, num = 4
		tlist = db.pcwltime.find({"datetime":{"$gte":data["start_time"]}}).sort("datetime", ASCENDING).limit(num)
		route_info = [] # 経路情報の取り出し
		route_info += db.pcwlroute.find({"$and": [
													{"query" : data["start_node"]}, 
													{"query" : data["end_node"]}
												]})
		route_info = optimize_direction(data["start_node"],data["end_node"],route_info[0]["dlist"])
		print("[出発点,到着点] = "+str([data["start_node"], data["end_node"]])+" , 間隔 = "+str(interval)+" 秒")

		# 重み付け用の計算
		if len(route_info) > 1:
			d_total = 0 #全経路の総距離
			for route in route_info:
				for node in route:
					d_total += node["distance"]
			add_total = 0
			for route in route_info:
				d_route = 0 #一つの経路の距離
				for node in route:
					d_route += node["distance"]
				tmp_add = (d_total - d_route) / d_total / (len(route_info) - 1)
				add_total += tmp_add * tmp_add

		if num >= 1:
			for route in route_info: # ある経路に対して以下を実行

				# 抜けている出発到着情報の補完
				if num > 1:
					total_distance = 0 # 経路の合計距離
					for node in route:
						total_distance += node["distance"]
					tmp_distance = 0 # 推定に用いる一時累計距離
					st_ed_info = [] # 欠落した出発到着情報を補完するリスト
					n_count = 0 # ノード情報のカウンター
					t_count = 1 # タイム情報のカウンター
					while t_count < num:
						tmp_distance += route[n_count]["distance"]
						if tmp_distance >= (total_distance*t_count/num): # 一時累計距離がしきい値を超えたら以下を実行
							if len(st_ed_info) == 0:
								st = data["start_node"]
							else :
								st = st_ed_info[-1]["ed"]
							extra_distance = tmp_distance - (total_distance*t_count/num)
							if extra_distance >= (route[n_count]["distance"]/2):
								ed = route[n_count]["direction"][0]
							else :
								ed = route[n_count]["direction"][1]
							st_ed_info.append({"st":st,"ed":ed})
							tmp_distance -= route[n_count]["distance"]
							t_count += 1
						else :
							n_count += 1
					st_ed_info.append({"st":st_ed_info[-1]["ed"],"ed":data["end_node"]}) # st_ed_infoの完成,例：[{'ed': 2, 'st': 1}, {'ed': 3, 'st': 2}]
				elif num == 1:
					st_ed_info = [{"st":data["start_node"],"ed":data["end_node"]}]
				print("st_ed_info = "+str(st_ed_info))

				# この経路の重みを計算
				if len(route_info) == 1:
					add = 1
				else:
					tmp_add = (d_total - total_distance) / d_total / (len(route_info) - 1)
					add = tmp_add * tmp_add / add_total
				print("add = "+str(add))

				# pfv情報の登録
				for j in range(0,num):
					if st_ed_info[j]["st"] != st_ed_info[j]["ed"]: # j番目の時刻において出発点到着点が同じ場合は以下をスキップ
						tmp_plist = db.pfvinfo.find_one({"datetime":{"$eq":tlist[j]["datetime"]}})
						if tmp_plist == None: # この時間の情報がまだDBに登録されていない場合
							make_empty_pfvinfo(tlist[j]["datetime"]) # この時間の空の情報を作成
							tmp_plist = db.pfvinfo.find_one({"datetime":{"$eq":tlist[j]["datetime"]}})
						j_route_info = [] # j番目の時刻の経路情報
						j_route_info += db.pcwlroute.find({"$and": [
																	{"query" : st_ed_info[j]["st"]}, 
																	{"query" : st_ed_info[j]["ed"]}
																	]})
						j_route_info = optimize_direction(st_ed_info[j]["st"],st_ed_info[j]["ed"],j_route_info[0]["dlist"])
						for j_route in j_route_info: # routeの例：[{'direction': [2, 3], 'distance': 75.16648189186454}, {'direction': [3, 4], 'distance': 69.6419413859206}]
							for node in j_route:
								tmp_plist["plist"][pfvinfo_id[node["direction"][0]][node["direction"][1]]]["size"] += add
						db.pfvinfo.save(tmp_plist)
					print(str(tlist[j]["datetime"])+"のpfvinfoを登録完了, 経路分岐 = "+str(len(route_info)))

		db.pfvinfo.create_index([("datetime", ASCENDING)])

# 滞留端末情報stayinfo関係
def make_empty_stayinfo(dt): # 空のstayinfoを作成
	# print(str(dt)+"の空のstayinfoを作成")
	plist = []
	for node in _pcwlnode:
		plist.append({"pcwl_id":node["pcwl_id"],"size":0,"mac_list":[]})
	db.stayinfo.insert({'datetime':dt,'plist':plist})

def make_stayinfo(dataset):
	# stayinfoを初期化
	db.stayinfo.remove()

	for data in dataset:
		interval = round(data["interval"])
		num = round(interval / 10) # 40秒間隔の場合, num = 4
		tlist = db.pcwltime.find({"datetime":{"$gte":data["start_time"]}}).sort("datetime", ASCENDING).limit(num)

		for i in range(0,num):

			# 残留端末情報の一時データ取り出し
			tmp_plist = db.stayinfo.find_one({"datetime":{"$eq":tlist[i]["datetime"]}})
			if tmp_plist == None: # この時間の情報がまだDBに登録されていない場合
				make_empty_stayinfo(tlist[i]["datetime"]) # この時間の空の情報を作成
				tmp_plist = db.stayinfo.find_one({"datetime":{"$eq":tlist[i]["datetime"]}})

			# 残留端末情報更新
			tmp_plist["plist"][stayinfo_id[data["start_node"]]]["size"] += 1
			tmp_plist["plist"][stayinfo_id[data["start_node"]]]["mac_list"] += [data["mac"]]
			db.stayinfo.save(tmp_plist)
		print(str(data["start_time"])+" interval = "+str(interval)+" node = "+str(data["start_node"])+" 保存")


# 6F実験関係
def make_empty_pfvinfoexperiment(dt): # 空のpfvinfoを作成
	print(str(dt)+"の空のpfvinfoexperimentを作成")
	plist = []
	# ノード同士の全組み合わせで経路情報を記録
	for i in range(0,len(_pcwlnode)):
		for j in range(0,len(_pcwlnode)):
			st = _pcwlnode[i]["pcwl_id"] # 出発点
			ed = _pcwlnode[j]["pcwl_id"] # 到着点
			# iとjが隣接ならば人流0人でplistに加える
			if ed in _pcwlnode[i]["next_id"]:
				plist.append({"direction":[st,ed],"size":0,"mac_list":[]})
	db.pfvinfoexperiment.insert({'datetime':dt,'plist':plist})

def make_pfvinfoexperiment(dataset):
	# 開始時にDBを初期化
	db.pfvinfoexperiment.remove()

	for data in dataset:
		interval = round(data["interval"])
		num = round(interval / 10) # 40秒間隔の場合, num = 4
		tlist = db.pcwltime.find({"datetime":{"$gte":data["start_time"]}}).sort("datetime", ASCENDING).limit(num)
		route_info = [] # 経路情報の取り出し
		route_info += db.pcwlroute.find({"$and": [
													{"query" : data["start_node"]}, 
													{"query" : data["end_node"]}
												]})
		route_info = optimize_direction(data["start_node"],data["end_node"],route_info[0]["dlist"])
		print("[出発点,到着点] = "+str([data["start_node"], data["end_node"]])+" , 間隔 = "+str(interval)+" 秒")

		# 重み付け用の計算
		if len(route_info) > 1:
			d_total = 0 #全経路の総距離
			for route in route_info:
				for node in route:
					d_total += node["distance"]
			add_total = 0
			for route in route_info:
				d_route = 0 #一つの経路の距離
				for node in route:
					d_route += node["distance"]
				tmp_add = (d_total - d_route) / d_total / (len(route_info) - 1)
				add_total += tmp_add * tmp_add

		if num >= 1:
			for route in route_info: # ある経路に対して以下を実行

				# 抜けている出発到着情報の補完
				if num > 1:
					total_distance = 0 # 経路の合計距離
					for node in route:
						total_distance += node["distance"]
					tmp_distance = 0 # 推定に用いる一時累計距離
					st_ed_info = [] # 欠落した出発到着情報を補完するリスト
					n_count = 0 # ノード情報のカウンター
					t_count = 1 # タイム情報のカウンター
					while t_count < num:
						tmp_distance += route[n_count]["distance"]
						if tmp_distance >= (total_distance*t_count/num): # 一時累計距離がしきい値を超えたら以下を実行
							if len(st_ed_info) == 0:
								st = data["start_node"]
							else :
								st = st_ed_info[-1]["ed"]
							extra_distance = tmp_distance - (total_distance*t_count/num)
							if extra_distance >= (route[n_count]["distance"]/2):
								ed = route[n_count]["direction"][0]
							else :
								ed = route[n_count]["direction"][1]
							st_ed_info.append({"st":st,"ed":ed})
							tmp_distance -= route[n_count]["distance"]
							t_count += 1
						else :
							n_count += 1
					st_ed_info.append({"st":st_ed_info[-1]["ed"],"ed":data["end_node"]}) # st_ed_infoの完成,例：[{'ed': 2, 'st': 1}, {'ed': 3, 'st': 2}]
				elif num == 1:
					st_ed_info = [{"st":data["start_node"],"ed":data["end_node"]}]
				print("st_ed_info = "+str(st_ed_info))

				# この経路の重みを計算
				if len(route_info) == 1:
					add = 1
				else:
					tmp_add = (d_total - total_distance) / d_total / (len(route_info) - 1)
					add = tmp_add * tmp_add / add_total
				print("add = "+str(add))

				# pfv情報の登録
				for j in range(0,num):
					if st_ed_info[j]["st"] != st_ed_info[j]["ed"]: # j番目の時刻において出発点到着点が同じ場合は以下をスキップ
						tmp_plist = db.pfvinfoexperiment.find_one({"datetime":{"$eq":tlist[j]["datetime"]}})
						if tmp_plist == None: # この時間の情報がまだDBに登録されていない場合
							make_empty_pfvinfoexperiment(tlist[j]["datetime"]) # この時間の空の情報を作成
							tmp_plist = db.pfvinfoexperiment.find_one({"datetime":{"$eq":tlist[j]["datetime"]}})
						j_route_info = [] # j番目の時刻の経路情報
						j_route_info += db.pcwlroute.find({"$and": [
																	{"query" : st_ed_info[j]["st"]}, 
																	{"query" : st_ed_info[j]["ed"]}
																	]})
						j_route_info = optimize_direction(st_ed_info[j]["st"],st_ed_info[j]["ed"],j_route_info[0]["dlist"])
						for j_route in j_route_info: # routeの例：[{'direction': [2, 3], 'distance': 75.16648189186454}, {'direction': [3, 4], 'distance': 69.6419413859206}]
							for node in j_route:
								tmp_plist["plist"][pfvinfo_id[node["direction"][0]][node["direction"][1]]]["size"] += add
								tmp_plist["plist"][pfvinfo_id[node["direction"][0]][node["direction"][1]]]["mac_list"] += [data["mac"]]
						db.pfvinfoexperiment.save(tmp_plist)
					print(str(tlist[j]["datetime"])+"のpfvinfoexperimentを登録完了, 経路分岐 = "+str(len(route_info)))

		db.pfvinfoexperiment.create_index([("datetime", ASCENDING)])
		
# 出発時刻、出発点、到着時刻、到着点のデータセット
# dataset = []
# dataset.append({"mac":"a","start_node":1,"start_time":datetime.datetime(2015,6,3,12,10,4),"end_node":11,"end_time":datetime.datetime(2015,6,3,12,10,54),"interval":50})
# dataset.append({"mac":"b","start_node":5,"start_time":datetime.datetime(2015,6,3,12,10,24),"end_node":9,"end_time":datetime.datetime(2015,6,3,12,10,54),"interval":30})
# dataset.append({"mac":"c","start_node":13,"start_time":datetime.datetime(2015,6,3,12,10,54),"end_node":9,"end_time":datetime.datetime(2015,6,3,12,11,4),"interval":10})
# dataset.append({"mac":"d","start_node":1,"start_time":datetime.datetime(2015,6,3,12,11,4),"end_node":5,"end_time":datetime.datetime(2015,6,3,12,11,14),"interval":10})
# dataset.append({"mac":"e","start_node":1,"start_time":datetime.datetime(2015,6,3,12,10,14),"end_node":5,"end_time":datetime.datetime(2015,6,3,12,10,44),"interval":30})

# import time
# start = time.time()
# make_pfvinfo(dataset)
# end = time.time()
# print("time:"+str(end-start))

print("エラー無しやな")