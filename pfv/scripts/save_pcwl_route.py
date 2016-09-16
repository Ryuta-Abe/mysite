import datetime
import math

# mongoDBに接続
from mongoengine import *
connect('nm4bd')

# PCWLの経路情報
class pcwlroute(Document):
    query = ListField(IntField())
    dlist = ListField(ListField(DictField()))
    floor = StringField()

    # meta = {
    #     "db_alias" : "nm4bd",
    # }

# 一旦初期化(位置情報全削除)
pcwlroute.objects.all().delete()

# 位置情報保存
def save_pcwlroute(q,d,f):
	_pcwlroute = pcwlroute(
		query = q,
		dlist = d,
		floor = f,
		)
	_pcwlroute.save()


# PCWLのノード情報
class pcwlnode(Document):
    pcwl_id = IntField()
    pos_x = IntField()
    pos_y = IntField()
    next_id = ListField(IntField())
    floor = StringField()

# PCWLノード情報取り出し
_pcwlnode = []
_pcwlnode += pcwlnode.objects()

# pcwl_idから登録順を求められるように(pcwlnode_id[pcwl_id] = i )
_pcwlnode_id = [0]*99
for i in range(0,len(_pcwlnode)):
	_pcwlnode_id[_pcwlnode[i]["pcwl_id"]] = i


# 経路を探索する際に再帰的に用いる関数
def route_search(route_list,ed):
	for n in _pcwlnode[_pcwlnode_id[route_list[-1]]]["next_id"]:
		if n not in route_list: # 一度通った道は再度通らない制約
			if n == ed:
				print("route_list = "+str(route_list+[n]))
				all_route_list.append(route_list+[n])
			else :
				route_search(route_list+[n],ed)

# 最短やそれに近い経路のみに絞り込む
def distance_filtering(all_route_list):
	fil = 1.5 # 最短から1.5倍までの距離は許容
	min_d = 99999999
	dlist = []
	for route_list in all_route_list:
		total_d = 0
		tmp_list = [] # 一時的に経路と距離を記録
		for i in range(0,len(route_list)-1):
			s = _pcwlnode_id[route_list[i]]
			e = _pcwlnode_id[route_list[i+1]]
			dis = math.sqrt(pow(_pcwlnode[s]["pos_x"]-_pcwlnode[e]["pos_x"],2)+pow(_pcwlnode[s]["pos_y"]-_pcwlnode[e]["pos_y"],2))
			total_d += dis
			tmp_list.append({"distance":dis,"direction":[route_list[i],route_list[i+1]]})
		if total_d < min_d * fil : # 合計距離が最短かそれに近い場合、以下を実行
			if total_d * fil < min_d: # これまでの記録よりも圧倒的に短い場合
				dlist = [tmp_list] # これまでの記録を消去し、新たにdlistを作成
				min_d = total_d # 最小距離を更新
			elif total_d < min_d : # これまでの記録と同じくらい短い場合は以下のどちらか
				dlist.append(tmp_list) # どちらのデータもdlistに残す
				min_d = total_d
			else :
				dlist.append(tmp_list)
	return dlist

# PCWLノード情報取り出し
_pcwlnode = []
_pcwlnode += pcwlnode.objects()

# pcwl_idから登録順を求められるように(pcwlnode_id[pcwl_id] = i )
_pcwlnode_id = [0]*99
for i in range(0,len(_pcwlnode)):
	_pcwlnode_id[_pcwlnode[i]["pcwl_id"]] = i

floor_list = ["W2-6F","W2-7F","W2-8F","W2-9F","kaiyo"]
for floor_str in floor_list:
	_pcwlnode = []
	_pcwlnode += pcwlnode.objects(floor = floor_str)
	_pcwlnode_id = [0]*99
	for i in range(0,len(_pcwlnode)):
		_pcwlnode_id[_pcwlnode[i]["pcwl_id"]] = i
	# ノード同士の全組み合わせで経路情報を記録
	for i in range(0,len(_pcwlnode)):
		for j in range(i+1,len(_pcwlnode)):
			st = _pcwlnode[i]["pcwl_id"] # 出発点
			ed = _pcwlnode[j]["pcwl_id"] # 到着点
			# iとjが隣接ならばそれを登録
			if ed in _pcwlnode[i]["next_id"]:
				dis = math.sqrt(pow(_pcwlnode[i]["pos_x"]-_pcwlnode[j]["pos_x"],2)+pow(_pcwlnode[i]["pos_y"]-_pcwlnode[j]["pos_y"],2))
				save_pcwlroute([st,ed],[[{'direction':[st,ed],'distance':dis}]],floor_str)
			# iとjが隣接ではない場合
			else :
				all_route_list = []
				route_list = [st]
				route_search(route_list,ed)
				dlist = distance_filtering(all_route_list)
				save_pcwlroute([st,ed],dlist,floor_str)

# 経路情報取り出しテスト
A = []
A += pcwlroute.objects(query__all=[1,3])
print("query = "+str(A[0].query)+" dlist = "+str(A[0].dlist))

print("エラー無しやな")