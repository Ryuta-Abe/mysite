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

# W2-8F nodes
save_pcwlnode(1,x,y,[2],"W2-8F")
save_pcwlnode(2,x,y,[1,3],"W2-8F")
save_pcwlnode(3,x,y,[2,4],"W2-8F")
save_pcwlnode(4,x,y,[5,17],"W2-8F")
save_pcwlnode(5,x,y,[4,7],"W2-8F")
save_pcwlnode(6,x,y,[7],"W2-8F")
save_pcwlnode(7,x,y,[5,6,8],"W2-8F")
save_pcwlnode(8,x,y,[7,10],"W2-8F")
save_pcwlnode(9,x,y,[10],"W2-8F")
save_pcwlnode(10,x,y,[8,9,15],"W2-8F")
save_pcwlnode(11,x,y,[12,18],"W2-8F")
save_pcwlnode(12,x,y,[11,13],"W2-8F")
save_pcwlnode(13,x,y,[12,14,17],"W2-8F")
save_pcwlnode(14,x,y,[13,15],"W2-8F")
save_pcwlnode(15,x,y,[10,14,16],"W2-8F")
save_pcwlnode(16,x,y,[15,18],"W2-8F")
save_pcwlnode(17,x,y,[4,13,19],"W2-8F")
save_pcwlnode(18,x,y,[11,16],"W2-8F")
save_pcwlnode(19,x,y,[17],"W2-8F")
#室内は全て隣接とした（暫定）
#20~23は室内（828号室）
save_pcwlnode(20,x,y,[21,22,23],"W2-8F")
save_pcwlnode(21,x,y,[20,22,23],"W2-8F")
save_pcwlnode(22,x,y,[20,21,23],"W2-8F")
save_pcwlnode(23,x,y,[20,21,22],"W2-8F")
#24~28は室内（809号室）
save_pcwlnode(24,x,y,[25,26,27,28],"W2-8F")
save_pcwlnode(25,x,y,[24,26,27,28],"W2-8F")
save_pcwlnode(26,x,y,[24,25,27,28],"W2-8F")
save_pcwlnode(27,x,y,[24,25,26,28],"W2-8F")
save_pcwlnode(28,x,y,[24,25,26,27],"W2-8F")

# W2-9F nodes
save_pcwlnode(1,x,y,[2],"W2-9F")
save_pcwlnode(2,x,y,[1,3],"W2-9F")
save_pcwlnode(3,x,y,[2,4],"W2-9F")
save_pcwlnode(4,x,y,[3,5],"W2-9F")
save_pcwlnode(5,x,y,[4,6,24],"W2-9F")
save_pcwlnode(6,x,y,[5,7,10],"W2-9F")
save_pcwlnode(7,x,y,[6,8],"W2-9F")
save_pcwlnode(8,x,y,[7,25,27],"W2-9F")
save_pcwlnode(9,x,y,[],"W2-9F")        #室内（925号室）
save_pcwlnode(10,x,y,[6],"W2-9F")
save_pcwlnode(11,x,y,[12,25],"W2-9F")
save_pcwlnode(12,x,y,[11,13,26],"W2-9F")
save_pcwlnode(13,x,y,[12],"W2-9F")
save_pcwlnode(14,x,y,[15],"W2-9F")
save_pcwlnode(15,x,y,[14,17,26],"W2-9F")
save_pcwlnode(16,x,y,[17,18],"W2-9F")
save_pcwlnode(17,x,y,[15,16],"W2-9F")
save_pcwlnode(18,x,y,[16,19,27],"W2-9F")
save_pcwlnode(19,x,y,[18,20,21],"W2-9F")
save_pcwlnode(20,x,y,[21],"W2-9F")
save_pcwlnode(21,x,y,[19,22],"W2-9F")
save_pcwlnode(22,x,y,[21,23,24],"W2-9F")
save_pcwlnode(23,x,y,[22],"W2-9F")
save_pcwlnode(24,x,y,[5,22],"W2-9F")
save_pcwlnode(25,x,y,[8,11],"W2-9F")
save_pcwlnode(26,x,y,[12,15],"W2-9F")
save_pcwlnode(27,x,y,[8,18],"W2-9F")


print("エラー無しやな")