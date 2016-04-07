# -*- coding: utf-8 -*-
import urllib.request
import datetime
import sys
import time
import socket

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
def dt_from_iso_to_numlong(dt):
	dt = str(dt.year)+("0"+str(dt.month))[-2:]+("0"+str(dt.day))[-2:]+("0"+str(dt.hour))[-2:]+("0"+str(dt.minute))[-2:]+("00"+str(dt.second))[-2:]
	return int(dt)

# node_id番のPCWLにコマンドを投げてhtml解析後DB登録
def save_rttmp(ip,node_id,user,pswd):	
	# Basic認証用のパスワードマネージャーを作成
	LOGIN_URL = "http://"+ip+"/ja/private/nmsetinfo"
	username = user
	password = pswd
	password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, LOGIN_URL, username, password)

	# openerの作成とインストール
	# HTTPS通信とBasic認証用のHandlerを使用
	opener = urllib.request.build_opener(urllib.request.HTTPSHandler(),
	                              urllib.request.HTTPBasicAuthHandler(password_mgr))
	urllib.request.install_opener(opener)

	html = []
	try:
		# urlopenのdata引数を指定するとHTTP/POSTを送信できる
		with urllib.request.urlopen(url=LOGIN_URL, data=b'cmd=/usr/sbin/station_list%20-i%20ath0', timeout=0.2) as page:
		    for line in page.readlines():
		        html.append(line.decode('utf-8'))

		if db.tscache.find({"node_id":node_id}).count() == 0:
			ts_cache = [{"th":0,"node_id":node_id}]
		else:
			ts_cache = db.tscache.find({"node_id":node_id}).sort("_id",-1).limit(1)
		ts_th = ts_cache[0]["th"]

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
					db.tscache.insert({"th":time_stamp,"node_id":node_id})
					first = False
				if time_stamp > ts_th:
					new_data = {"node_id":node_id,"get_time_no":now,"mac":mac,"rssi":rssi,"dbm":rssi - 95}
					data_list.append(new_data)
				else :
					break
			if "Station Count:" in line:
				dbsave_flag = True
	except urllib.error.URLError:
		print("Timeout "+ip)
	except socket.timeout:
		print("Socket Timeout "+ip)
	
# db.rttmp.remove() # 一旦DBを空に
now = dt_from_iso_to_numlong(datetime.datetime.today()) # 現在時刻を取得し14桁の数字列に変換

st = time.time()
data_list = []

# 6Fのデータ収集
pcwliplist = []
# search_floor = ["W2-6F","W2-7F"]
search_floor = ["kaiyo"]
for floor in search_floor:
	pcwliplist += db.pcwliplist.find({"floor":floor})

user = "root"
pswd = ""
for pcwlip in pcwliplist:
	save_rttmp(pcwlip["ip"],pcwlip["node_id"],user,pswd)

if len(data_list) > 1:
	db.rttmp.insert(data_list)
	db.rttmp2.insert(data_list)

ed = time.time()
print(ed-st)

# print("エラー無しやな")