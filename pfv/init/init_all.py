"""
MongoDBインストール後に初回のみ実行
PCWLの初期情報を以下のDBに追加する

pcwliplist: floor,pcwl_idとIPアドレスの対応関係
pcwlnode: floor,pcwl_idと存在位置（x,y座標）の対応関係
pcwlroute: floorとpcwl_idの移動ベクトルquery(ex:[1,24])の対応関係が全パターン
idealroute: pcwlrouteのうち、それぞれの移動距離が最小のもの
"""

# -*- coding: utf-8 -*-
# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from init_db import init_db
from make_pcwliplist import *
from make_pcwlnode import *
from make_pcwlroute import *


if __name__ == '__main__':
    init_db()
    make_pcwliplist()
    make_pcwlnode()
    make_pcwlroute()
    # print("Please execute 'python3 ./save_pcwl_route.py'")
    # save_route()
    # os.system("python3 save_pcwl_route.py")
