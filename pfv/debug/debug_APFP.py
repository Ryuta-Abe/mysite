# -*- coding: utf-8 -*-

## 使い方　##
# 0. csv_examine_routeの指定事項（db.csvtestのインポート、解析対象クエリ指定）を確認
# 1. debug_all db.trtmpにインポートするjsonファイルのパス　（解析開始時刻）　（解析終了時刻）　を実行
from time import time
st = time()
import os, sys, itertools, csv, shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
from pymongo import *
client = MongoClient()
db = client.nm4bd
import pandas as pd
from statistics import mean
from init_all import init_all
from csv_examine_route import make_exp_id
from make_pcwlnode import delete_part_pcwlnode
from classify import get_deleted_rssi_list
from make_model import make_model
from debug_all import debug_all
import config
from utils import get_m_from_px

### TODO:以下を変更 ###
### config.pyの各種パラメーターを変更  ###
# AP_RANGE = range(14,27)
# FP_RANGE = range(13,54)
# FP_RANGE = [14, 39]
# FP_RANGE = range(27, 54)
# AP_RANGE, FP_RANGE = range(19,27,2), range(13,54)
AP_RANGE, FP_RANGE = [19], range(46,54,3)
# AP_RANGE, FP_RANGE = [16], [50]
AP_DELETE_ORDER = config.AP_DELETE_ORDER
MIDPOINT_DELETE_ORDER = config.MIDPOINT_DELETE_ORDER  # len: MIDPOINT_FP_COUNT - AP_COUNT
# FP_DELETE_LIST = AP_DELETE_ORDER
import_flag = True  # trtmp, csvtestにインポートしなおすかどうか
DATE = "20190413"
ST_DT = DATE + "2149"
# ED_DT = DATE + "2153"
ED_DT = DATE + "2334" ## 解析終了時刻 """
ST_EXP_ID = 1  # 開始クエリ番号
# ED_EXP_ID = 4
ED_EXP_ID = 96 # 終了クエリ番号
###
FLOOR = "W2-7F"  # TODO：一般化
AP_COUNT = 26
MIDPOINT_FP_COUNT = 53  # 中点を含むFP数
PATH =  "../../working/"
AP_COUNT_TRAIN_FILE = "190611_W2-7F_train.csv"
MIDPOINT_FP_COUNT_TRAIN_FILE = FLOOR +"_train.csv"
# MIDPOINT_FP_DELETE_LIST = []  # len: MIDPOINT_FP_COUNT - AP_COUNT
# INI_FILE = "../config.ini"
# ini = ConfigParser()
# if os.path.exists(INI_FILE):
# 	ini.read(INI_FILE, encoding = "utf-8")
# AP_DELETE_ORDER = ini.get("AP_FP", "AP_DELETE_ORDER")


def make_deleted_train_file(input_file_name,output_file_name, AP_delete_list,FP_delete_list):
	input_label_file_name = input_file_name.replace("train","label")
	col_names = [node["pcwl_id"] for node in db.reg_pcwlnode.find({"floor":FLOOR})] #Name the column
	df_train = pd.read_csv(PATH + input_file_name, engine='python', names=col_names)
	if type(FP_delete_list[0]) is int:  # 削除
		df_label = pd.read_csv(PATH + input_label_file_name, engine='python', names=["label"])
	else:	
		df_label = pd.read_csv(PATH + input_label_file_name, engine='python', names=["label"], dtype = str)
	df_list = [df_train, df_label]
	df = pd.concat(df_list, axis = 1)
	# print(df)
	if len(AP_delete_list) > 0:
		df = df.drop(AP_delete_list, axis = 1) # 列(特徴量)を削除
	if len(FP_delete_list) > 0:
		df = df[~df["label"].isin(FP_delete_list)]  # 行を削除
	# df = df.drop("label",axis = 1)  # ラベルを削除
	df_label = df["label"]
	df_train = df.drop("label",axis = 1)  # ラベルを削除

	# 結果train, label ファイルをCSVに出力
	output_label_file_name = output_file_name.replace("train","label") 
	df_label.to_csv(PATH + output_label_file_name, encoding='utf_8', header = None, index = None)
	df_train.to_csv(PATH + output_file_name, encoding='utf_8', header = None, index = None)
	# old ver.
	# with open(PATH + input_file, 'r') as f:
	# 	doc = [row for row in csv.reader(f, delimiter=',')]
	# for i, row in enumerate(doc):
	# 	doc[i] = get_deleted_rssi_list(FLOOR,row,AP_DELETE_LIST)
	# with open(PATH + output_file, 'w') as f:
	# 	w = csv.writer(f, delimiter=',', lineterminator='\n')  #列区切りと行区切りの文字を指定
	# 	w.writerows(doc)

def debug_APFP():
	# global MIDPOINT_FP_DELETE_LIST
	def import_file():
		short_DATE = DATE[2:]
		query_list = make_exp_id(short_DATE + '_', ST_EXP_ID, ED_EXP_ID)  
		json_file_name = "rttmp3_" + DATE + ".json" 
		json_file = PATH + json_file_name
		param_file_name = "exp_param_" + DATE + ".csv" 
		param_file = PATH + param_file_name
		os.system("mongoimport -d nm4bd -c trtmp " + json_file + " --drop")
		os.system("mongoimport -d nm4bd -c csvtest --headerline --columnsHaveTypes --type=csv " + param_file + " --drop")
		return query_list

	def output_result():
		# 結果を出力
		output_file_name = DATE + "_AP" + str(AP) + "_FP" + str(FP) + ".csv"
		output_file = PATH + output_file_name
		command = 'mongoexport --sort {"exp_id":1} -d nm4bd -c examine_summary -o '+output_file+' --type=csv --fieldFile ../../mlfile/txt/exp_result.txt'
		os.system(command)
	# def get_output_file_name():
		# file_name = "AP" + AP + "_" + "FP" + FP + "_W2-7F_train.csv"
	# def move_ML_file(train_file_name, label_file_name):
	# 	MLFILE_PATH = "../../mlfile/csv/"
	# 	shutil.move(PATH + train_file_name, MLFILE_PATH + train_file_name)
	# 	shutil.move(PATH + label_file_name, MLFILE_PATH + label_file_name)
	def backup_model(floor, AP, FP):
		ML_FILE_PATH = "../../mlmodel/"
		shutil.copy(ML_FILE_PATH + floor + "_model.pkl", ML_FILE_PATH + "backup/" + "AP" + str(AP) + "_FP" + str(FP) + "_" + floor + "_model.pkl")

	db.debug_APFP.drop()
	query_list = []
	for i, (AP, FP) in enumerate(itertools.product(AP_RANGE, FP_RANGE)):
		init_all()  # DB初期化, PCWL関係DB追加
		print("------------ AP: ", AP,"FP: ", FP, " ------------")
		if i == 0:  # 初回のみPRデータとexp_paramをインポート
			query_list = import_file()
		### TODO: input_fileの変更
		#AP数,FP数を調整したtrain fileを作成
		AP_delete_num = AP_COUNT - AP
		AP_delete_list = AP_DELETE_ORDER[:AP_delete_num]
		FP_delete_num = AP_COUNT - FP
		if AP_delete_num < 0:
			print("Error: AP_delete_num < 0")
			raise ValueError

		if FP_delete_num >= 0:  # FPをAP数以下にする場合
			# TODO: pcwl_nodeからの抹消
			FP_delete_list = AP_DELETE_ORDER[:FP_delete_num]
			delete_part_pcwlnode(FLOOR, FP_delete_list)
			input_file = AP_COUNT_TRAIN_FILE
			# label_file = AP_COUNT_LABEL_FILE
			contains_midpoint = False
			config.set_CONTAINS_MIDPOINT(contains_midpoint)
			# config.set_value(ini, "AP_FP", "CONTAINS_MIDPOINT", contains_midpoint)
			# config.set_value(ini, "AP_FP", "MARGIN_RATIO", 2)
		else:  # FPをAP数よりも増やす(中点を加える)場合
			double_FP_delete_num = MIDPOINT_FP_COUNT - FP  # 中点を含む(AP数の約2倍)train fileから何個のラベルを削除するか
			FP_delete_list = MIDPOINT_DELETE_ORDER[:double_FP_delete_num]
			input_file = MIDPOINT_FP_COUNT_TRAIN_FILE
			# label_file = MIDPOINT_FP_COUNT_LABEL_FILE
			contains_midpoint = True
			config.set_CONTAINS_MIDPOINT(contains_midpoint)
			# config.set_value(ini, "AP_FP", "CONTAINS_MIDPOINT", contains_midpoint)
			# config.set_value(ini, "AP_FP", "MARGIN_RATIO", 4)
		output_file = "AP" + str(AP) + "_" + "FP" + str(FP) + "_W2-7F_train.csv"
		make_deleted_train_file(input_file,output_file, AP_delete_list,FP_delete_list)
		label_file = output_file.replace("train","label")
		# move_ML_file(output_file, label_file)  # mlfileフォルダにtrain, labelファイルを移動
		make_model(output_file, label_file, contains_midpoint)
		backup_model(FLOOR, AP, FP)
		# 設定ファイルconfigの変更
		# config.DELETES_FP = False
		if AP_delete_num > 0:
			config.set_DELETES_AP_FP(True, False)
			config.set_AP_DELETE_NUM(AP_delete_num)
			# config.set_value(ini, "AP_FP", "DELETES_AP", True)
			# config.set_value(ini, "AP_FP", "DELETES_FP", False)
			# config.set_value(ini, "AP_FP", "AP_DELETE_NUM", AP_delete_num)
			# config.show_config(ini)
		else:
			config.set_DELETES_AP_FP(False, False)
			# config.set_value(ini, "AP_FP", "DELETES_AP", False)
			# config.set_value(ini, "AP_FP", "DELETES_FP", False)

		debug_all(ST_DT,ED_DT,query_list)
		pipe = [{ '$group' : { '_id': 'null', 'average': { '$avg': '$avg_err_dist[m]'}}}]
		agg = db.examine_summary.aggregate(pipeline = pipe)["result"]
		average_error_distance = agg[0]["average"]
		pipe = [{ '$group' : { '_id': 'null', 'average': { '$avg': '$accuracy'}}}]
		agg = db.examine_summary.aggregate(pipeline = pipe)["result"]
		average_accuracy = agg[0]["average"]
		db.debug_APFP.insert({"AP":AP,"FP":FP,"avg_err_dist":average_error_distance, "avg_accuracy": average_accuracy})

		# # 結果を出力
		output_result()
## mongoexport -d nm4bd -c debug_APFP --type=csv -o result.csv -f AP,FP,avg_err_dist,avg_accuracy
def get_theoretical_err_dist():
	# for i, (AP, FP) in enumerate(itertools.product(AP_RANGE, FP_RANGE)):
	# 	init_all()
	# 	# AP_delete_num = AP_COUNT - AP
	# 	# AP_delete_list = AP_DELETE_ORDER[:AP_delete_num]
	# 	FP_delete_num = AP_COUNT - FP
	# 	# if AP_delete_num < 0:
	# 	# 	print("Error: AP_delete_num < 0")
	# 	# 	raise ValueError

	# 	if FP_delete_num >= 0:  # FPを全AP数以下にする場合
	def exists_midpoint(FP_midpoint_list, pcwl_id_1, pcwl_id_2):
		midpoint = str(pcwl_id_1) + "." + str(pcwl_id_2)
		if midpoint in FP_midpoint_list:
			return True
		midpoint = str(pcwl_id_2) + "." + str(pcwl_id_1)
		if midpoint in FP_midpoint_list:
			return True
		else:
			return False

	for FP in FP_RANGE:
		init_all()  # DB初期化, PCWL関係DB追加
		FP_delete_num = AP_COUNT - FP
		if FP_delete_num >= 0:  # FPを全AP数以下にする場合
			FP_delete_list = AP_DELETE_ORDER[:FP_delete_num]
			delete_part_pcwlnode(FLOOR, FP_delete_list)
			pcwlnode_list = db.pcwlnode.find({"floor": FLOOR})
			average_distance_list = []
			for pcwlnode in pcwlnode_list:
				next_id_list = pcwlnode["next_id"]
				next_distance_list = []
				for next_id in next_id_list:
					next_distance = db.idealroute.find_one({"$and": [{"floor" : FLOOR},{"query" : pcwlnode["pcwl_id"]},{"query" : next_id}]})["total_distance"]
					next_distance_list.append(next_distance)
				average_distance_list.append(mean(next_distance_list))
			average_distance = get_m_from_px(mean(average_distance_list))
		else:
			double_FP_delete_num = MIDPOINT_FP_COUNT - FP  # 中点を含む(AP数の約2倍)train fileから何個のラベルを削除するか
			FP_midpoint_list = MIDPOINT_DELETE_ORDER[double_FP_delete_num:]  # 残ったFPに含まれる中点のリスト
			if len(FP_midpoint_list) != FP - AP_COUNT:
				print("ERROR")
			# FP_delete_list = AP_DELETE_ORDER[:FP_delete_num]
			# delete_part_pcwlnode(FLOOR, FP_delete_list)
			pcwlnode_list = db.reg_pcwlnode.find({"floor": FLOOR})
			average_distance_list = []
			if "9.1" in FP_midpoint_list:
				index = FP_midpoint_list.index("9.1")
				FP_midpoint_list[index] = "9.10"
			if "18.2" in FP_midpoint_list:
				index = FP_midpoint_list.index("18.2")
				FP_midpoint_list[index] = "18.20"
			for pcwlnode in pcwlnode_list:
				next_id_list = pcwlnode["next_id"]
				next_distance_list = []
				for next_id in next_id_list:
					next_distance = db.idealroute.find_one({"$and": [{"floor" : FLOOR},{"query" : pcwlnode["pcwl_id"]},{"query" : next_id}]})["total_distance"]
					if exists_midpoint(FP_midpoint_list, pcwlnode["pcwl_id"], next_id):
						next_distance = next_distance / 2
					next_distance_list.append(next_distance)
				average_distance_list.append(mean(next_distance_list))
			for midpoint in FP_midpoint_list:
				pcwl_id_list = midpoint.split(".")
				pcwl_id_1 = int(pcwl_id_list[0])
				pcwl_id_2 = int(pcwl_id_list[1])
				next_distance = db.idealroute.find_one({"$and": [{"floor" : FLOOR},{"query" : pcwl_id_1},{"query" : pcwl_id_2}]})["total_distance"]
				average_distance_list.append(next_distance/2)  # 中点から隣接するAPまでの距離の平均
			average_distance = get_m_from_px(mean(average_distance_list))
		db.theo_err.insert({"FP":FP, "avg_err":average_distance})


if __name__ == '__main__':
	debug_APFP()
	# get_theoretical_err_dist()
	# input_file = "190611_W2-7F_train.csv"
	# output_file = "APtest"  + "_" + "FPtest"  + "_W2-7F_train.csv"
	# make_deleted_train_file(input_file,output_file,AP_DELETE_LIST,FP_DELETE_LIST)
