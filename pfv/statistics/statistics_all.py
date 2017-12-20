# -*- coding: utf-8 -*-

from time import time
st = time()

# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from analyze_sta import analyze_mod
from convert_datetime import dt_from_14digits_to_iso
from remake_data import data_sorting

from pymongo import *
client = MongoClient()
db = client.nm4bd

def statistics_all(st_dt, ed_dt): #ローカルでのみ使用、サーバ上では使用しない
    mac = []
    mac += db.trtmp.find({"get_time_no":{"$gte":st_dt,"$lte":ed_dt}}).distinct("mac") # データ作成に用いるmacのみの過去データをリセットする
    ### DB初期化 ##############
    for i in mac:
        db.pastdata.remove({"mac":i})
    db.pcwltime.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.pfvinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.pfvmacinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.stayinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.staymacinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})

    analyze_mod(st_dt,ed_dt)

def db_clear(st_dt, ed_dt):
    ### 対象期間の該当データのみ除去（重複防止） ##############
    db.pastdata.drop()
    db.pcwltime.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.pfvinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.pfvmacinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.stayinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.staymacinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.modpfvinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})
    db.modstayinfo.remove({"datetime":{"$gte":st_dt,"$lte":ed_dt}})

if __name__ == '__main__':
    # st_dt = 20171212185000
    # ed_dt = 20171212185500
    st_dt = 20171024164400
    ed_dt = 20171024170500
    # st_dt = 20171128163730
    # ed_dt = 20171128165030
    # st_dt = 20171206174000
    # ed_dt = 20171206175500
    # st_dt = 20171208161500
    # ed_dt = 20171208163000
    # 時刻をiso形式に変換
    st_dt = dt_from_14digits_to_iso(st_dt)
    ed_dt = dt_from_14digits_to_iso(ed_dt)
    # db_clear(st_dt, ed_dt)
    # statistics_all(st_dt, ed_dt)
    data_sorting(st_dt, ed_dt)
    print(time() - st)
