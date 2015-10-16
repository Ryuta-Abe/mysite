import datetime
import math

# mongoDBに接続
from mongoengine import *
from pymongo import *

from pfv.models import pcwlnode, pfvinfo, pfvinfoexperiment, pcwlroute, pcwltime, stayinfo

client = MongoClient()
db = client.nm4bd

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
_pcwlnode += pcwlnode.objects()

# 位置情報保存
def save_pfvinfo(p,d):
	_pfvinfo = pfvinfo(
		plist = p,
		datetime = d
		)
	_pfvinfo.save()

# 空のpfvinfoを作成
def make_empty_pfvinfo(dt):
	print(str(dt)+"の空のpfvinfoを作成")
	plist = []
	# ノード同士の全組み合わせで経路情報を記録
	for i in range(0,len(_pcwlnode)):
		for j in range(0,len(_pcwlnode)):
			st = _pcwlnode[i]["pcwl_id"] # 出発点
			ed = _pcwlnode[j]["pcwl_id"] # 到着点
			# iとjが隣接ならば人流0人でplistに加える
			if ed in _pcwlnode[i]["next_id"]:
				plist.append({"direction":[st,ed],"size":0})
	save_pfvinfo(plist,dt)

# st,edに対して人数追加
def add_size(st,ed,add,tmp_plist):
	output = []
	for i in range(0,len(tmp_plist)): # iの例：{ "size" : 0, "direction" : [ 8, 24 ] }
		if tmp_plist[i]["direction"] == [st,ed]:
			output.append({"direction":tmp_plist[i]["direction"],"size":(tmp_plist[i]["size"] + add)})
		else:
			output.append(tmp_plist[i])
	return output

# 経路情報の向きを最適化(st > edの場合にリストとdirectionの中身を逆向きに)
def optimize_direction(st,ed,route_info):
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
	pfvinfo.objects.all().delete()

	for data in dataset:
		interval = round(data["interval"])
		num = round(interval / 10) # 40秒間隔の場合, num = 4
		tlist = pcwltime.objects(datetime__gte = data["start_time"]).order_by("datetime").limit(num).scalar("datetime")
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
						tmp_plist = []
						tmp_plist += pfvinfo.objects(datetime = tlist[j]).scalar("plist")
						if len(tmp_plist) == 0: # この時間の情報がまだDBに登録されていない場合
							make_empty_pfvinfo(tlist[j]) # この時間の空の情報を作成
							tmp_plist += pfvinfo.objects(datetime = tlist[j]).scalar("plist")
						tmp_plist = tmp_plist[0]
						j_route_info = [] # j番目の時刻の経路情報
						j_route_info += db.pcwlroute.find({"$and": [
																	{"query" : st_ed_info[j]["st"]}, 
																	{"query" : st_ed_info[j]["ed"]}
																	]})
						j_route_info = optimize_direction(st_ed_info[j]["st"],st_ed_info[j]["ed"],j_route_info[0]["dlist"])
						for j_route in j_route_info: # routeの例：[{'direction': [2, 3], 'distance': 75.16648189186454}, {'direction': [3, 4], 'distance': 69.6419413859206}]
							for node in j_route:
								tmp_plist = add_size(node["direction"][0],node["direction"][1],add,tmp_plist)
								pfvinfo.objects(datetime = tlist[j]).delete()
								save_pfvinfo(tmp_plist,tlist[j])
					print(str(tlist[j])+"のpfvinfoを登録完了, 経路分岐 = "+str(len(route_info)))

# 滞留端末情報保存
def save_stayinfo(p,d):
	_stayinfo = stayinfo(
		plist = p,
		datetime = d
		)
	_stayinfo.save()

# 空のstayinfoを作成
def make_empty_stayinfo(dt):
	print(str(dt)+"の空のstayinfoを作成")
	plist = []
	for node in _pcwlnode:
		plist.append({"pcwl_id":node["pcwl_id"],"size":0,"mac_list":[]})
	save_stayinfo(plist,dt)

def add_staysize(node_id,mac,tmp_plist):
	output = []
	for i in range(0,len(tmp_plist)): # iの例：{ "size" : 0, "direction" : [ 8, 24 ] }
		if tmp_plist[i]["pcwl_id"] == node_id:
			output.append({"pcwl_id":tmp_plist[i]["pcwl_id"]
				,"size":(tmp_plist[i]["size"] + 1)
				,"mac_list":(tmp_plist[i]["mac_list"]+[mac])
				})
		else:
			output.append(tmp_plist[i])
	return output

def make_stayinfo(dataset):
	stayinfo.objects.all().delete()

	for data in dataset:
		interval = round(data["interval"])
		num = round(interval / 10) # 40秒間隔の場合, num = 4
		tlist = pcwltime.objects(datetime__gte = data["start_time"]).order_by("datetime").limit(num).scalar("datetime")

		for i in range(0,num):

			# 残留端末情報の一時データ取り出し
			tmp_plist = []
			tmp_plist += stayinfo.objects(datetime = tlist[i]).scalar("plist")
			if len(tmp_plist) == 0: # この時間の情報がまだDBに登録されていない場合
				make_empty_stayinfo(tlist[i]) # この時間の空の情報を作成
				tmp_plist += stayinfo.objects(datetime = tlist[i]).scalar("plist")
			tmp_plist = tmp_plist[0]

			# 残留端末情報更新
			tmp_plist = add_staysize(data["start_node"],data["mac"],tmp_plist)
			stayinfo.objects(datetime = tlist[i]).delete()
			save_stayinfo(tmp_plist,tlist[i])


# 6F実験関係
# 位置情報保存
def save_pfvinfo_experiment(p,d):
	_pfvinfo_experiment = pfvinfoexperiment(
		plist = p,
		datetime = d
		)
	_pfvinfo_experiment.save()

# 空のpfvinfoを作成
def make_empty_pfvinfo_experiment(dt):
	print(str(dt)+"の空のpfvinfoexperimentを作成")
	plist = []
	# ノード同士の全組み合わせで経路情報を記録
	for i in range(0,len(_pcwlnode)):
		for j in range(0,len(_pcwlnode)):
			st = _pcwlnode[i]["pcwl_id"] # 出発点
			ed = _pcwlnode[j]["pcwl_id"] # 到着点
			# iとjが隣接ならば人流0人でplistに加える
			if ed in _pcwlnode[i]["next_id"]:
				plist.append({"direction":[st,ed],"size":0})
	save_pfvinfo_experiment(plist,dt)

def make_pfvinfo_experiment(dataset):
	# 開始時にDBを初期化
	pfvinfoexperiment.objects.all().delete()

	for data in dataset:
		interval = round(data["interval"])
		num = round(interval / 10) # 40秒間隔の場合, num = 4
		tlist = pcwltime.objects(datetime__gte = data["start_time"]).order_by("datetime").limit(num).scalar("datetime")
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
						tmp_plist = []
						tmp_plist += pfvinfoexperiment.objects(datetime = tlist[j]).scalar("plist")
						if len(tmp_plist) == 0: # この時間の情報がまだDBに登録されていない場合
							make_empty_pfvinfo_experiment(tlist[j]) # この時間の空の情報を作成
							tmp_plist += pfvinfoexperiment.objects(datetime = tlist[j]).scalar("plist")
						tmp_plist = tmp_plist[0]
						j_route_info = [] # j番目の時刻の経路情報
						j_route_info += db.pcwlroute.find({"$and": [
																	{"query" : st_ed_info[j]["st"]}, 
																	{"query" : st_ed_info[j]["ed"]}
																	]})
						j_route_info = optimize_direction(st_ed_info[j]["st"],st_ed_info[j]["ed"],j_route_info[0]["dlist"])
						for j_route in j_route_info: # routeの例：[{'direction': [2, 3], 'distance': 75.16648189186454}, {'direction': [3, 4], 'distance': 69.6419413859206}]
							for node in j_route:
								tmp_plist = add_size(node["direction"][0],node["direction"][1],add,tmp_plist)
								pfvinfoexperiment.objects(datetime = tlist[j]).delete()
								save_pfvinfo_experiment(tmp_plist,tlist[j])
					print(str(tlist[j])+"のpfvinfoexperimentを登録完了, 経路分岐 = "+str(len(route_info)))
			

# # 出発時刻、出発点、到着時刻、到着点のデータセット
# dataset = []
# dataset.append({"mac":"a","start_node":1,"start_time":datetime.datetime(2015,6,3,12,10,4),"end_node":11,"end_time":datetime.datetime(2015,6,3,12,10,54),"interval":50})
# dataset.append({"mac":"b","start_node":5,"start_time":datetime.datetime(2015,6,3,12,10,24),"end_node":9,"end_time":datetime.datetime(2015,6,3,12,10,54),"interval":30})
# dataset.append({"mac":"c","start_node":13,"start_time":datetime.datetime(2015,6,3,12,10,54),"end_node":9,"end_time":datetime.datetime(2015,6,3,12,11,4),"interval":10})
# dataset.append({"mac":"d","start_node":1,"start_time":datetime.datetime(2015,6,3,12,11,4),"end_node":5,"end_time":datetime.datetime(2015,6,3,12,11,14),"interval":10})

# make_pfvinfo_experiment(dataset)

print("エラー無しやな")