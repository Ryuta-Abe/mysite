import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
from pymongo import *
client = MongoClient()
db = client.nm4bd
from statistics import mean
# from configparser import ConfigParser
import pandas as pd
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
# FPのデータ数を半分にするか(26⇒13)
DELETES_FP = True
## FPの教師データ数を半分にするか(26⇒13)
DELETES_AP = True
if CONTAINS_MIDPOINT:
	MARGIN_RATIO = 4
else:
	MARGIN_RATIO = 2
## AP_DELETE_ORDER = ['18.20', '12.14', '10.11', '6.24', '4.5', '14.15', '15.16', '16.17', '3.4', '8.25', '1.2', '12.26', '21.23', '16.27', '2.3', '5.23', '17.18', '9.26', '8.27', '9.25', '5.6', '21.22', '6.7', '9.10', '7.8', '12.13', '20.21']	
AP_DELETE_ORDER = [14, 24, 15, 4, 2, 23, 17, 20, 25, 26, 27, 10, 6]  ## TODO: 一個消しすぎ, labelからは消していない
AP_DELETE_NUM = 999
MIDPOINT_DELETE_ORDER = ['12.14', '10.11', '6.24', '4.5', '14.15', '15.16', '16.17', '3.4', '8.25', '1.2', '12.26', '21.23', '16.27', '2.3', '5.23', '17.18', '9.26', '8.27', '9.25', '5.6', '21.22', '6.7', '7.8', '12.13', '20.21', '18.2', '9.1']
FP = 999
## TODO: 9.1, 18.2になっていることによる距離の増大解決
def get_AP_DELETE_ORDER(floor):
	AP_DELETE_ORDER =  [2,4,6,10,14,15,17,20,23,24,25,26,27]
	average_distance_list = []
	for pcwl_id in AP_DELETE_ORDER:
		node_info = db.pcwlnode.find_one({"floor":floor,"pcwl_id":pcwl_id})
		next_id_list = node_info["next_id"]
		next_distance_list = []
		for next_id in next_id_list:
			next_distance = db.idealroute.find_one({"$and": [{"floor" : floor},{"query" : pcwl_id},{"query" : next_id}]})["total_distance"]
			next_distance_list.append(next_distance)
		average_distance_list.append(mean(next_distance_list))
	# print(average_distance_list)
	ziped_list = zip(AP_DELETE_ORDER,average_distance_list)
	ziped_list = sorted(ziped_list,key = lambda x:x[1])
	AP_DELETE_ORDER = [x[0] for x in ziped_list]
	return AP_DELETE_ORDER

def get_MIDPOINT_DELETE_ORDER(floor):
	PATH = "../../working/"
	MIDPOINT_FP_COUNT_TRAIN_FILE = floor + "_train.csv"
	MIDPOINT_FP_COUNT_LABEL_FILE = MIDPOINT_FP_COUNT_TRAIN_FILE.replace("train","label")
	df = pd.read_csv(PATH + MIDPOINT_FP_COUNT_LABEL_FILE, engine='python', names=["label"],dtype = str)
	midpoint_list = [label for label in df["label"].unique() if "." in label]
	distance_list = [] 
	for midpoint in midpoint_list:
		if midpoint == '18.2':
			midpoint = '18.20'
			index = midpoint_list.index("18.2")
			midpoint_list[index] = "18.20"
		if midpoint == '9.1':
			midpoint = '9.10'
			index = midpoint_list.index("9.1")
			midpoint_list[index] = "9.10"

		st_node = int(midpoint.split(".")[0])
		ed_node = int(midpoint.split(".")[1])		
		distance = db.idealroute.find_one({"$and": [{"floor" : floor},{"query" : st_node},{"query" : ed_node}]})["total_distance"]
		distance_list.append(distance)
	ziped_list = zip(midpoint_list,distance_list)
	ziped_list = sorted(ziped_list,key = lambda x:x[1])
	MIDPOINT_DELETE_ORDER = [x[0] for x in ziped_list]
	print(MIDPOINT_DELETE_ORDER)
	return MIDPOINT_DELETE_ORDER

def set_AP_DELETE_NUM(AP_delete_num):
	global AP_DELETE_NUM
	AP_DELETE_NUM = AP_delete_num

def set_CONTAINS_MIDPOINT(contains_midpoint):
	global CONTAINS_MIDPOINT, MARGIN_RATIO
	CONTAINS_MIDPOINT = contains_midpoint
	if CONTAINS_MIDPOINT:
		MARGIN_RATIO = 4
	else:
		MARGIN_RATIO = 2	

def set_DELETES_AP_FP(deletes_AP, deletes_FP):
	global DELETES_AP, DELETES_FP
	DELETES_AP, DELETES_FP = deletes_AP, deletes_FP

def set_FP(fp):
    global FP
    FP = fp

def read_config_file(ini_file):
	ini = ConfigParser()
	if os.path.exists(ini_file):
		ini.read(ini_file, encoding = "utf-8")
	return ini
	# AP_DELETE_ORDER = ini.get("AP_FP", "AP_DELETE_ORDER")


def show_config(ini):
    '''
    設定ファイルの全ての内容を表示する（コメントを除く）
    '''
    for section in ini.sections():
        print ('[%s]' % (section))
        show_section(ini, section)
    return


def show_section(ini, section):
    '''
    設定ファイルの特定のセクションの内容を表示する
    '''
    for key in ini.options(section):
        show_key(ini, section, key)
    return


def show_key(ini, section, key):
    '''
    設定ファイルの特定セクションの特定のキー項目（プロパティ）の内容を表示する
    '''
    print ('%s.%s =%s' % (section, key, ini.get(section, key)))
    return


def set_value(ini, section, key, value):
    '''
    設定ファイルの特定セクションの特定のキー項目（プロパティ）の内容を変更する
    '''
    ini.set(section, key, value)
    print ('set %s.%s =%s' % (section, key, ini.get(section, key)))
    return


def usage():
    sys.stderr.write("Usage: %s inifile [section [key [value]]]\n" % sys.argv[0])
    return


if __name__ == '__main__':
    # argc = len(sys.argv)
    # if argc == 1:
    #     usage()
    #     sys.exit(1)

    # # 設定ファイル読み込み
    # INI_FILE = sys.argv[1]
    # ini = ConfigParser()
    # if os.path.exists(INI_FILE):
    #     ini.read(INI_FILE, encoding = "utf-8")
    # else:
    #     sys.stderr.write('%s が見つかりません' % INI_FILE)
    #     sys.exit(2)

    # if argc == 2:
    #     show_config(ini)
    # elif argc == 3:
    #     show_section(ini, sys.argv[2])
    # elif argc == 4:
    #     show_key(ini, sys.argv[2], sys.argv[3])
    # elif argc == 5:
    #     set_value(ini, sys.argv[2], sys.argv[3], sys.argv[4])
    #     # ファイルに書き出す（注意！現状だとコメントや改行を消してしまいます）
    #     f = open(INI_FILE, "w")
    #     ini.write(f)
    #     f.close()
    # else:
    #     usage()
    #     sys.exit(3)

    # sys.exit(0)

	get_MIDPOINT_DELETE_ORDER("W2-7F")



# if __name__ == "__main__":
# 	# get_AP_DELETE_ORDER("W2-7F")