import datetime

# mongoDBに接続
from mongoengine import *
connect('nm4bd')

# クラスの定義
class pcwlnode(Document):
    pcwl_id = IntField()
    pos_x = IntField()
    pos_y = IntField()
    next_id = ListField(IntField())

# 一旦初期化(位置情報全削除)
pcwlnode.objects.all().delete()

# 位置情報保存
def save_pcwlnode(id,x,y,t):
	_pcwlnode = pcwlnode(
		pcwl_id = id,
		pos_x = x,
		pos_y = y,
		next_id = t
		)
	_pcwlnode.save()

save_pcwlnode(1,990,130,[2])
save_pcwlnode(2,920,150,[1,3])
save_pcwlnode(3,925,225,[2,4])
save_pcwlnode(4,860,200,[3,5])
save_pcwlnode(5,800,200,[4,6,22])
save_pcwlnode(6,700,190,[5,7,23])
save_pcwlnode(7,590,180,[6,8])
save_pcwlnode(8,470,180,[7,24,27])
save_pcwlnode(9,300,180,[10,12,27])
save_pcwlnode(10,190,200,[9,11])
save_pcwlnode(11,130,200,[10])
save_pcwlnode(12,300,350,[9,13,14])
save_pcwlnode(13,180,340,[12])
save_pcwlnode(14,350,340,[12,15])
save_pcwlnode(15,410,330,[14,16])
save_pcwlnode(16,475,350,[15,17,24])
save_pcwlnode(17,540,330,[16,18])
save_pcwlnode(18,630,325,[17,19])
save_pcwlnode(19,670,340,[18,20])
save_pcwlnode(20,790,350,[19,21,22])
save_pcwlnode(21,900,350,[20])
save_pcwlnode(22,790,275,[5,20])
save_pcwlnode(23,700,250,[6])
save_pcwlnode(24,480,275,[8,16])
save_pcwlnode(27,400,180,[8,9])

print("エラー無しやな")