# -*- coding: utf-8 -*-
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
    floor = StringField()

# 一旦初期化(位置情報全削除)
pcwlnode.objects.all().delete()

# 位置情報保存
def save_pcwlnode(id,x,y,t,f):
	_pcwlnode = pcwlnode(
		pcwl_id = id,
		pos_x = x,
		pos_y = y,
		next_id = t,
		floor = f
		)
	_pcwlnode.save()

# W2-6F nodes
save_pcwlnode(1,990,130,[2],"W2-6F")
save_pcwlnode(2,920,150,[1,3],"W2-6F")
save_pcwlnode(3,925,225,[2,4],"W2-6F")
save_pcwlnode(4,860,200,[3,5],"W2-6F")
save_pcwlnode(5,800,200,[4,6,22],"W2-6F")
save_pcwlnode(6,700,190,[5,7,23],"W2-6F")
save_pcwlnode(7,590,180,[6,8],"W2-6F")
save_pcwlnode(8,470,180,[7,24,27],"W2-6F")
save_pcwlnode(9,300,180,[10,12,27],"W2-6F")
save_pcwlnode(10,190,200,[9,11],"W2-6F")
save_pcwlnode(11,130,200,[10],"W2-6F")
save_pcwlnode(12,300,350,[9,13,14],"W2-6F")
save_pcwlnode(13,180,340,[12],"W2-6F")
save_pcwlnode(14,350,340,[12,15],"W2-6F")
save_pcwlnode(15,410,330,[14,16],"W2-6F")
save_pcwlnode(16,475,350,[15,17,24],"W2-6F")
save_pcwlnode(17,540,330,[16,18],"W2-6F")
save_pcwlnode(18,630,325,[17,19],"W2-6F")
save_pcwlnode(19,670,340,[18,20],"W2-6F")
save_pcwlnode(20,790,350,[19,21,22],"W2-6F")
save_pcwlnode(21,900,350,[20],"W2-6F")
save_pcwlnode(22,790,275,[5,20],"W2-6F")
save_pcwlnode(23,700,250,[6],"W2-6F")
save_pcwlnode(24,480,275,[8,16],"W2-6F")
save_pcwlnode(27,400,180,[8,9],"W2-6F")

# W2-7F nodes
save_pcwlnode(1,990,130,[2],"W2-7F")
save_pcwlnode(2,920,150,[1,3],"W2-7F")
save_pcwlnode(3,925,225,[2,4],"W2-7F")
save_pcwlnode(4,860,200,[3,5],"W2-7F")
save_pcwlnode(5,800,200,[4,6,23],"W2-7F")
save_pcwlnode(6,700,190,[5,7,24],"W2-7F")
save_pcwlnode(7,590,180,[6,8],"W2-7F")
save_pcwlnode(8,470,180,[7,25,27],"W2-7F")
save_pcwlnode(9,300,180,[10,25,26],"W2-7F")
save_pcwlnode(10,190,200,[9,11],"W2-7F")
save_pcwlnode(11,130,200,[10],"W2-7F")
save_pcwlnode(12,300,350,[26,13,14],"W2-7F")
save_pcwlnode(13,180,340,[12],"W2-7F")
save_pcwlnode(14,350,340,[12,15],"W2-7F")
save_pcwlnode(15,410,330,[14,16],"W2-7F")
save_pcwlnode(16,475,350,[15,17,27],"W2-7F")
save_pcwlnode(17,540,330,[16,18],"W2-7F")
save_pcwlnode(18,630,325,[17,20],"W2-7F")
save_pcwlnode(20,670,340,[18,21],"W2-7F")
save_pcwlnode(21,790,350,[20,22,23],"W2-7F")
save_pcwlnode(22,900,350,[21],"W2-7F")
save_pcwlnode(23,790,275,[5,21],"W2-7F")
save_pcwlnode(24,700,250,[6],"W2-7F")
save_pcwlnode(25,400,180,[8,9],"W2-7F")
save_pcwlnode(26,300,275,[9,12],"W2-7F")
save_pcwlnode(27,480,275,[8,16],"W2-7F")

# kaiyo nodes
save_pcwlnode(1,100,150,[2,9,10],"kaiyo")
save_pcwlnode(2,300,150,[1,11,8,9,10],"kaiyo")
# save_pcwlnode(3,550,150,[2,4,8,9],"kaiyo")
save_pcwlnode(4,900,150,[11,5],"kaiyo")
save_pcwlnode(5,900,300,[4,6,8],"kaiyo")
save_pcwlnode(6,900,500,[5,7],"kaiyo")
save_pcwlnode(7,600,500,[6,8],"kaiyo")
save_pcwlnode(8,675,350,[2,11,7,9,5],"kaiyo")
save_pcwlnode(9,300,300,[1,2,11,8,10],"kaiyo")
save_pcwlnode(10,100,300,[1,2,9],"kaiyo")
save_pcwlnode(11,550,150,[2,4,8,9],"kaiyo")

print("エラー無しやな")