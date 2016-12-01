# -*- coding: utf-8 -*-
import time
all_st = time.time()
import urllib.request
import datetime
import sys
import socket
from multiprocessing import Pool
from multiprocessing import Process
import os
from convert_datetime import *
from analyze import analyze_mod
import timeout_decorator # cannot use on Windows

# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

# db.rttmp.remove() # 一旦DBを空に
db.trtmp.remove() # 一旦DBを空に

now = datetime.datetime.today()
now = iso_to_end05iso(now)
user = "root"
pswd = ""
data_list = {}

#トラッキング用のMACアドレスリスト（値は暫定）
tag_list = ["00:11:81:10:01:1c",
			"00:11:81:10:01:19",
			"00:11:81:10:01:17",
			"00:11:81:10:01:1a",
			"00:11:81:10:01:23",
			"00:11:81:10:01:1b"]

# 6Fのデータ収集
pcwliplist = []
search_floor = ["W2-6F","W2-7F","W2-9F"] # exclude W2-8F
#search_floor = ["kaiyo"]

for floor in search_floor:
	pcwliplist.extend(db.pcwliplist.find({"floor":floor,"parallel_num":{"$ne":999}},{"_id":False, "node_id":False}).sort("parallel_num",1))

### using functions ###
def make_empty_maccache(num):
	mac_cache = {"node_id":{}}
	for pcwlip in pcwliplist:
		mac_cache.update({str(pcwlip["node_id"]):{}}) # {"mac":time_stamp}
	for i in range(0,num):
		db.maccache.insert(mac_cache)

# ipアドレスがipのPCWLにコマンドを投げてhtml解析後DB登録
def save_rttmp(ip,floor,pcwl_id):
	data_list = [] #type:[{}]
	to_list = []
	# Basic認証用のパスワードマネージャーを作成
	LOGIN_URL = "http://"+ip+"/ja/private/nmsetinfo"
	password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, LOGIN_URL, user, pswd)

	# openerの作成とインストール
	# HTTPS通信とBasic認証用のHandlerを使用
	opener = urllib.request.build_opener(urllib.request.HTTPSHandler(),
	                              urllib.request.HTTPBasicAuthHandler(password_mgr))
	urllib.request.install_opener(opener)

	html = []
	try:
		# urlopenのdata引数を指定するとHTTP/POSTを送信できる
		with urllib.request.urlopen(url=LOGIN_URL, data=b'cmd=/usr/sbin/station_list%20-i%20ath0', timeout=0.5) as page:
		    for line in page.readlines():
		        html.append(line.decode('utf-8'))

		if db.tscache.find({"ip":ip}).count() == 0:
			ts_cache = [{"th":0,"ip":ip}]
		else:
			# remove node_id , add : ip
			ts_cache = db.tscache.find({"ip":ip}).sort("_id",-1).limit(1)
		ts_th = ts_cache[0]["th"] #type:int, store old time_stamp

		dbsave_flag = False
		first = True
		for line in html:
			if dbsave_flag:
				if "--- END RESULT ---" in line:
					break
				line_split = line.split()
				mac = line_split[0]
				rssi = int(line_split[1])
				time_stamp = int(line_split[3])
				if first:
					# db.tscache.insert({"th":time_stamp,"node_id":node_id})
					db.tscache.update({"ip":ip},{"$set": {"th":time_stamp, "ip":ip}}, True)
					first = False
				if time_stamp > ts_th:
					# add : floor, pcwl_id
					new_data = {"ip":ip,"get_time_no":now,"mac":mac, "rssi":rssi,"dbm":rssi - 95}
					# 8fとフォーマットを合わせるためfloor,pcwl_id delete
					# new_data = {"ip":ip,"get_time_no":now,"mac":mac, "floor":floor, "pcwl_id":pcwl_id, "rssi":rssi,"dbm":rssi - 95}
					# data_list.append(new_data)
					data_list.append(new_data)
					# print(type(data_list))
				else :
					break
			if "Station Count:" in line:
				dbsave_flag = True
	except urllib.error.URLError:
		# add : floor, pcwl_id
		# db.timeoutlog.insert({"datetime":now, "timeout_ip":ip, "floor":floor, "pcwl_id":pcwl_id, "TO_type":"Normal timeout"})
		to_data = {"datetime":now, "timeout_ip":ip, "floor":floor, "pcwl_id":pcwl_id, "TO_type":"Normal timeout"}
		to_list.append(to_data)
		# print(to_data)
		str_pid = ("  "+ str(pcwl_id))[-3:]
		print("Timeout : "+floor+str_pid+" "+ ip)
	except socket.timeout:
		# add : floor, pcwl_id
		# db.timeoutlog.insert({"datetime":now, "timeout_ip":ip, "floor":floor, "pcwl_id":pcwl_id, "TO_type":"Socket timeout"})
		sto_data = {"datetime":now, "timeout_ip":ip, "floor":floor, "pcwl_id":pcwl_id, "TO_type":"Socket timeout"}
		to_list.append(sto_data)
		# print(sto_data)
		str_pid = ("  "+ str(pcwl_id))[-3:]
		print("SocketTO: "+floor+str_pid+" "+ ip)
	return {"data_list":data_list,"to_list":to_list}


def save_function(pcwlip): #pcwlip: type:dict, elements: ip, floor, pcwl_id
	if (pcwlip["ip"] != "10.0.11.55"):
		#print ('process id:' + str(os.getpid())) #プロセス番号の表示（確認用）
		data_list = save_rttmp(pcwlip["ip"],pcwlip["floor"],pcwlip["pcwl_id"])
		# print(data_list)
		if len(data_list["data_list"]) >= 1:
			db.rttmp.insert(data_list["data_list"])
			db.rttmp3.insert(data_list["data_list"])
		if len(data_list["to_list"]) >= 1:
			db.timeoutlog.insert(data_list["to_list"])
			# print("-------------------Tolog was inserted----------------------")
		# return data_list
		for data in data_list["data_list"]:
			if data["mac"] in tag_list:
				db.trtmp.insert(data)
				# print("inserted.")


@timeout_decorator.timeout(4.0) # cannot use on Windows
def multi(pcwliplist):
	p = Pool(8) #プロセス数の選択
	data_list = p.map(save_function, pcwliplist)
	# 同期処理
	p.close()
	p.join()

# rounding in specified place
def rounding(num, round_place):
	rounded_num = round(num*pow(10, round_place)) / pow(10, round_place)
	return rounded_num


if __name__ == "__main__":
	st = time.time()
	### can not use on Windows ###
	try:
		multi(pcwliplist)
	except:
		print ("===== getPR timed out :( =====")
	else:
		pass
		# print ("getPR finished successfully :)")
	##############################
	
	# multi(pcwliplist)
	ed = time.time()
	print("getPR:"+str(rounding(ed-st,3))+"[sec]")

	### Check col_name trtmp or trtmp_test ###
	### when execute all process, uncomment under 5 lines. ###
	param = sys.argv
	st_dt = dt_end_to_05(str(param[1]))
	st_dt = dt_from_14digits_to_iso(st_dt)
	ed_dt = shift_seconds(st_dt, 5)
	analyze_mod(st_dt, ed_dt)
	print("Total:"+str(rounding(time.time()-all_st,3))+"[sec]")
	##########################################################