# -*- coding: utf-8 -*-
import urllib.request
import datetime
import sys
import time
import socket
from multiprocessing import Pool
from multiprocessing import Process
import os

from convert_datetime import *
from analyze import analyze_mod
# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

def make_empty_maccache(num):
	mac_cache = {"node_id":{}}
	for pcwlip in pcwliplist:
		mac_cache.update({str(pcwlip["node_id"]):{}}) # {"mac":time_stamp}
	for i in range(0,num):
		db.maccache.insert(mac_cache)

# isodate形式 --> numlong形式(20140405123456789)
#def dt_from_iso_to_numlong(dt):
#	dt = str(dt.year)+("0"+str(dt.month))[-2:]+("0"+str(dt.day))[-2:]+("0"+str(dt.hour))[-2:]+("0"+str(dt.minute))[-2:]+("00"+str(dt.second))[-2:]
#	return int(dt)

#def dt_from_14digits_to_iso(dt):
	#from datetime import datetime
#	dt = str(dt[0:4])+"-"+str("0"+dt[4:6])[-2:]+"-"+str("0"+dt[6:8])[-2:]+" "+str("00"+dt[8:10])[-2:]+":"+str("00"+dt[10:12])[-2:]+":"+str("00"+dt[12:14])[-2:]
#	dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
#	return dt

# ipアドレスがipのPCWLにコマンドを投げてhtml解析後DB登録
def save_rttmp(ip,floor,pcwl_id):
	data_list = [] #type:[{}]
	# Basic認証用のパスワードマネージャーを作成
	LOGIN_URL = "http://"+ip+"/ja/private/nmsetinfo"
	password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, LOGIN_URL, "root", "")

	# openerの作成とインストール
	# HTTPS通信とBasic認証用のHandlerを使用
	opener = urllib.request.build_opener(urllib.request.HTTPSHandler(),
	                              urllib.request.HTTPBasicAuthHandler(password_mgr))
	urllib.request.install_opener(opener)

	html = []
	try:
		# urlopenのdata引数を指定するとHTTP/POSTを送信できる
		with urllib.request.urlopen(url=LOGIN_URL, data=b'cmd=/usr/sbin/station_list%20-i%20ath0', timeout=0.5) as page:
		    #print (node_id)
		    #print (page.readlines())
		    for line in page.readlines():
		        html.append(line.decode('utf-8'))

		if db.tscache_test.find({"ip":ip}).count() == 0:
			ts_cache = [{"th":0,"ip":ip}]
		else:
			# remove node_id , add : ip
			ts_cache = db.tscache_test.find({"ip":ip}).sort("_id",-1).limit(1)
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
					db.tscache_test.update({"ip":ip},{"$set": {"th":time_stamp, "ip":ip}}, True) 
					first = False
				if time_stamp > ts_th:
					# add : floor, pcwl_id
					new_data = {"ip":ip,"get_time_no":now,"mac":mac, "rssi":rssi,"dbm":rssi - 95}
					# 8fとフォーマットを合わせるためfloor,pcwl_id delete
					# new_data = {"ip":ip,"get_time_no":now,"mac":mac, "floor":floor, "pcwl_id":pcwl_id, "rssi":rssi,"dbm":rssi - 95}
					# data_list.append(new_data)
					data_list.append(new_data)
					print(type(data_list))
				else :
					break
			if "Station Count:" in line:
				dbsave_flag = True
	except urllib.error.URLError:
		#log_dt = dt_from_14digits_to_iso(str(now))
		# add : floor, pcwl_id
		db.timeoutlog_test.insert({"datetime":now, "timeout_ip":ip, "floor":floor, "pcwl_id":pcwl_id, "TO_type":"Normal timeout"})
		print("Timeout "+ip)
	except socket.timeout:
		#log_dt = dt_from_14digits_to_iso(str(now))
		# add : floor, pcwl_id
		db.timeoutlog_test.insert({"datetime":now, "timeout_ip":ip, "floor":floor, "pcwl_id":pcwl_id, "TO_type":"Socket timeout"})
		print("Socket Timeout "+ip)
	return data_list

def save_function(pcwlip): #pcwlip: type:dict, elements: ip, floor, pcwl_id
	#print ('process id:' + str(os.getpid())) #プロセス番号の表示（確認用）
	data_list = save_rttmp(pcwlip["ip"],pcwlip["floor"],pcwlip["pcwl_id"])
	# print(data_list)
	if len(data_list) > 1:
			db.rttmp_test.insert(data_list)
			db.rttmp3_test.insert(data_list)
	# return data_list
	for data in data_list:
		if data["mac"] in tag_list:
			db.trtmp_test.insert(data)

def multi(pcwliplist):
	p = Pool(8) #プロセス数の選択
	data_list = p.map(save_function, pcwliplist)
	# print (data_list)
	# n = 0
	# while n < 51:
	# 	multi_list += data_list[n]
	# 	n += 2
	# #sorted(set(multi_list), key=multi_list.index)
	# print(len(multi_list))
	#print(multi_list)
	# i = 0
	# while i < 50:
	# 	print(len(data_list[i]))
	# 	print(len(data_list[i+1]))
	# 	print("=======================")
	# 	i += 2
	# return data_list

# multi_list =[]
# db.rttmp.remove() # 一旦DBを空に37v
#now = dt_from_iso_to_numlong(datetime.datetime.today()) # 現在時刻を取得し14桁の数字列に変換
now = datetime.datetime.today()
now = iso_to_end05iso(now)
# if __name__ == '__main__':
st = time.time()

#トラッキング用のMACアドレスリスト（値は暫定）
# tag_list = ["b0:65:bd:61:1f:f5","bc:6c:21:4d:fc:72","c","d"]
tag_list = ["00:11:81:10:01:1c","00:11:81:10:01:19","00:11:81:10:01:17","00:11:81:10:01:1a","00:11:81:10:01:23","00:11:81:10:01:1b"]
# data_list = []
# 6Fのデータ収集
pcwliplist = []
search_floor = ["W2-6F","W2-7F"]
#search_floor = ["kaiyo"]
for floor in search_floor:
	pcwliplist.extend(db.pcwliplist.find({"floor":floor},{"_id":False, "node_id":False}))
#user = "root"
#pswd = ""

# for pcwlip in pcwliplist:
# 	save_rttmp(pcwlip["ip"],pcwlip["node_id"],user,pswd)
if __name__ == '__main__':
	multi(pcwliplist)
	# print(data_list)
	# print("__main__func")
	#

# if len(multi_list) > 1:
	# db.rttmp.insert(multi_list)
	# for data in multi_list:
	# 	db.rttmp3.update({"node_id":data["node_id"],"mac":data["mac"],"get_time_no":data["get_time_no"]},
	# 									{"$setOnInsert": {"node_id":data["node_id"],"get_time_no":now,"mac":data["mac"],"rssi":data["rssi"],"dbm":data["rssi"] - 95}},
	# 									upsert=True)
	# rt.rttmp3.insert(data_list[0])
	# db.rttmp2.insert(multi_list)

ed = time.time()
print(ed-st)

### when execute all process, uncomment under 3 lines. ###
# ed_dt = dt_from_iso_to_str(now)[:14]
# st_de = shift_seconds(ed_dt, -5)
# analyze(st_dt, ed_dt)
