import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
from pymongo import *
client = MongoClient()
db = client.nm4bd

"""
解析方式のパラメータを指定
import configを読み込み前に書く
config.HOGEでアクセスできる
"""
### TODO:以下を実行前に入力 ###
USE_ML = True
## MEMO: FP数はラベル数, AP数は特徴量の数に相当
## FP(Fingerprint)に中点を含む(約2倍にする)か(マージンが半分になる)
CONTAINS_MIDPOINT = False
# FPの数を半分にするか(26⇒13)
DELETES_FP = True
## FPのデータ数を半分にするか(26⇒13)
DELETES_AP = True
if CONTAINS_MIDPOINT:
	MARGIN_RATIO = 4
else:
	MARGIN_RATIO = 2	
