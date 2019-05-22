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

def make_analyze_db():
    db.floor_analyze.drop()
    node_list = []
    node_list += db.pcwlnode.find()
    for node in node_list:
        if node["floor"] != "kaiyo" or node["floor"] != "W2-8F":
            go ={"total":0}
            come = {"total":0}
            transition = {}
            for id in node["next_id"]:
                go[str(id)] = 0
                come[str(id)] = 0
                transition[str(id)] = {"total":0}
                for destination in db.pcwlnode.find_one({"floor":node["floor"],"pcwl_id":id})["next_id"]:
                    transition[str(id)][str(destination)] = 0
            db.floor_analyze.insert({"floor":node["floor"],"pcwl_id":node["pcwl_id"],"go":go,"come":come,"transition":transition})

if __name__ == '__main__':
    # st_dt = 20171212185000
    # ed_dt = 20171212185500
    # st_dt = 20171024164400
    # ed_dt = 20171024170500
    # st_dt = 20171128163730
    # ed_dt = 20171128165030
    # st_dt = 20171206174000
    # ed_dt = 20171206175500
    # st_dt = 20171226154000
    # ed_dt = 20171226162500
    # st_dt = 20171226174000
    # ed_dt = 20171226181000
    # st_dt = 20180115141000
    # ed_dt = 20180115161000

    # st_dt = 20180115141000
    # ed_dt = 20180115161000

    # st_dt = 20180115162000
    # ed_dt = 20180115164500
    # ed_dt = 20180115171000

    # 実験用
    # 滞留実験///////////////////////////////////////////////////////////////////
    # st_dt = 20180131133000
    # ed_dt = 20180131203000
    # /////////////////////////////////////////////////////////////////////////

    # 移動実験（直線・ジグザグ）///////////////////////////////////////////////////////////////////
    # st_dt = 20180203171700
    # ed_dt = 20180203175300
    # /////////////////////////////////////////////////////////////////////////

    # 移動実験（周回）///////////////////////////////////////////////////////////////////
    # st_dt = 20180203191300
    # ed_dt = 20180203194500
    # /////////////////////////////////////////////////////////////////////////

    # 移動実験（6F直線）///////////////////////////////////////////////////////////////////
    # st_dt = 20180203171700
    # ed_dt = 20180203172400

    # 移動実験（7F直線）///////////////////////////////////////////////////////////////////
    # st_dt = 20180203172600
    # ed_dt = 20180203173200
    # /////////////////////////////////////////////////////////////////////////

    # 移動実験（7F直線 new）///////////////////////////////////////////////////////////////////
    st_dt = 20181226013500
    #ed_dt = 20181226022500 ## TODO: 戻す
    ed_dt = 20181226013700  ## tmp time for debug

    # 移動実験（6Fジグザグ）///////////////////////////////////////////////////////////////////
    # st_dt = 20180203173500
    # ed_dt = 20180203174200
    # /////////////////////////////////////////////////////////////////////////

    # 移動実験（7Fジグザグ）///////////////////////////////////////////////////////////////////
    # st_dt = 20180203174500
    # ed_dt = 20180203175300
    # /////////////////////////////////////////////////////////////////////////

    # 移動実験（6F周回）///////////////////////////////////////////////////////////////////
    # st_dt = 20180203191300
    # ed_dt = 20180203192900
    # /////////////////////////////////////////////////////////////////////////

    # 移動実験（7F周回）///////////////////////////////////////////////////////////////////
    # st_dt = 20180204144200
    # ed_dt = 20180204145630
    # /////////////////////////////////////////////////////////////////////////

    # 移動実験（フロア変更）///////////////////////////////////////////////////////////////////
    # st_dt = 20180204120500
    # ed_dt = 20180204121100
    # /////////////////////////////////////////////////////////////////////////

    # 6F移動＋滞留実験///////////////////////////////////////////////////////////////////
    # st_dt = 20180204150400
    # ed_dt = 20180204152225
    # /////////////////////////////////////////////////////////////////////////

    # 7F移動＋滞留実験///////////////////////////////////////////////////////////////////
    # st_dt = 20180204153100
    # ed_dt = 20180204154935
    # /////////////////////////////////////////////////////////////////////////

    # スマホ移動６F///////////////////////////////////////////////////////////////////
    # st_dt = 20180204193000
    # ed_dt = 20180204193330
    # /////////////////////////////////////////////////////////////////////////

    # スマホ移動６F///////////////////////////////////////////////////////////////////
    # st_dt = 20180204193600
    # ed_dt = 20180204194000
    # /////////////////////////////////////////////////////////////////////////

    # 時刻をiso形式に変換
    st_dt = dt_from_14digits_to_iso(st_dt)
    ed_dt = dt_from_14digits_to_iso(ed_dt)
    db_clear(st_dt, ed_dt)
    make_analyze_db()
    statistics_all(st_dt, ed_dt)
    data_sorting(st_dt, ed_dt)
    print(time() - st)
