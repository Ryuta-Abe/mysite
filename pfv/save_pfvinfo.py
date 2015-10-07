import datetime
import math

# mongoDBに接続
from mongoengine import *
connect('nm4bd')

# PCWLのノード情報
class pcwlnode(Document):
    pcwl_id = IntField()
    pos_x = IntField()
    pos_y = IntField()
    next_id = ListField(IntField())

# PCWLの経路情報
class pcwlroute(Document):
    query = ListField(IntField())
    dlist = ListField(ListField(DictField()))

    # meta = {
    #     "db_alias" : "nm4bd",
    # }

# 人流情報
class pfvinfo(Document):
    plist = ListField(DictField())
    datetime = DateTimeField()

    # meta = {
    #     "db_alias" : "nm4bd",
    # }

# 一旦初期化(位置情報全削除)
pfvinfo.objects.all().delete()

# 位置情報保存
def save_pfvinfo(p,d):
	_pfvinfo = pfvinfo(
		plist = p,
		datetime = d
		)
	_pfvinfo.save()

# PCWLノード情報取り出し
_pcwlnode = []
_pcwlnode += pcwlnode.objects()

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

	for data in dataset:
		interval = int(data["interval"])
		tmp_plist = []
		tmp_plist += pfvinfo.objects(datetime = data["start_time"]).scalar("plist")
		if len(tmp_plist) == 0: # この時間の情報がまだDBに登録されていない場合
			make_empty_pfvinfo(data["start_time"]) # この時間の空の情報を作成
			tmp_plist += pfvinfo.objects(datetime = data["start_time"]).scalar("plist")
		tmp_plist = tmp_plist[0]
		route_info = [] # 経路情報の取り出し
		route_info += pcwlroute.objects(query__all = [data["start_node"], data["end_node"]])
		route_info = optimize_direction(data["start_node"],data["end_node"],route_info[0]["dlist"])
		print("[出発点,到着点] = "+str([data["start_node"], data["end_node"]])+" , 間隔 = "+str(interval)+" 秒")

		# 10秒間隔の場合
		if interval == 10:
			for route in route_info: # routeの例：[{'direction': [2, 3], 'distance': 75.16648189186454}, {'direction': [3, 4], 'distance': 69.6419413859206}]
				for node in route:
					add = 1/len(route_info) # 足す人数(重み付けを考慮した小数の値,今はどの経路も同じ重み)
					tmp_plist = add_size(node["direction"][0],node["direction"][1],add,tmp_plist)
					pfvinfo.objects(datetime = data["start_time"]).delete()
					save_pfvinfo(tmp_plist,data["start_time"])
			print(str(data["start_time"])+"のpfvinfoを登録完了, 経路分岐 = "+str(len(route_info)))

		# 20秒以上の間隔の場合
		else:
			num = int(interval / 10) # 40秒間隔の場合, num = 4
			tlist = [data["start_time"], # tlistは時間情報のDBから取り出すように後で変える
					datetime.datetime(2014,11,10,11,10,19),
					datetime.datetime(2014,11,10,11,10,29),
					datetime.datetime(2014,11,10,11,10,39),
					datetime.datetime(2014,11,10,11,10,49)]

			for route in route_info: # ある経路に対して以下を実行

				# 抜けている出発到着情報の補完
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
				print("st_ed_info = "+str(st_ed_info))

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
						j_route_info += pcwlroute.objects(query__all = [st_ed_info[j]["st"], st_ed_info[j]["ed"]])
						j_route_info = optimize_direction(st_ed_info[j]["st"],st_ed_info[j]["ed"],j_route_info[0]["dlist"])
						for j_route in j_route_info: # routeの例：[{'direction': [2, 3], 'distance': 75.16648189186454}, {'direction': [3, 4], 'distance': 69.6419413859206}]
							for node in j_route:
								add = 1/len(route_info) # 足す人数(重み付けを考慮した小数の値,今はどの経路も同じ重み)
								tmp_plist = add_size(node["direction"][0],node["direction"][1],add,tmp_plist)
								pfvinfo.objects(datetime = tlist[j]).delete()
								save_pfvinfo(tmp_plist,tlist[j])
					print(str(tlist[j])+"のpfvinfoを登録完了, 経路分岐 = "+str(len(route_info)))

# 出発時刻、出発点、到着時刻、到着点のデータセット
dataset = []
dataset.append({"mac":"a","start_node":11,"start_time":datetime.datetime(2014,11,10,11,10,9),"end_node":1,"end_time":datetime.datetime(2014,11,10,11,10,59),"interval":50})
dataset.append({"mac":"b","start_node":1,"start_time":datetime.datetime(2014,11,10,11,10,9),"end_node":5,"end_time":datetime.datetime(2014,11,10,11,10,59),"interval":50})
dataset.append({"mac":"c","start_node":2,"start_time":datetime.datetime(2014,11,10,11,10,59),"end_node":4,"end_time":datetime.datetime(2014,11,10,11,11,9),"interval":10})
dataset.append({"mac":"d","start_node":4,"start_time":datetime.datetime(2014,11,10,11,11,9),"end_node":16,"end_time":datetime.datetime(2014,11,10,11,11,19),"interval":10})

# 保存テスト
make_pfvinfo(dataset)

print("エラー無しやな")