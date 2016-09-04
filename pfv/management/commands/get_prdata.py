# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import urllib.request
import datetime
import sys
import time
st = time.time()
import socket
from multiprocessing import Pool
from multiprocessing import Process
import os
from pfv.convert_datetime import dt_from_14digits_to_iso, dt_from_iso_to_numlong

# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd
# db.rttmp.remove() # 一旦DBを空に

user = "root"
pswd = ""
now = dt_from_iso_to_numlong(datetime.datetime.today()) # 現在時刻を取得し14桁の数字列に変換
data_list = {}

#トラッキング用のMACアドレスリスト（値は暫定）
tag_list = ["00:11:81:10:01:1c",
            "00:11:81:10:01:19",
            "00:11:81:10:01:17",
            "00:11:81:10:01:1a",
            "00:11:81:10:01:23",
            "00:11:81:10:01:1b"]

# 6,7Fのデータ収集
search_floor = ["W2-6F","W2-7F"]
#search_floor = ["kaiyo"]

class Command(BaseCommand):
  # args = '<target_id target_id ...>'
  help = u'django command test'

  def handle(self, *args, **options):

    pcwliplist = []
    for floor in search_floor:
        pcwliplist += db.pcwliplist.find({"floor":floor})
    multi(pcwliplist)
    ed = time.time()
    print(ed-st)


def make_empty_maccache(num):
    mac_cache = {"node_id":{}}
    for pcwlip in pcwliplist:
        mac_cache.update({str(pcwlip["node_id"]):{}}) # {"mac":time_stamp}
    for i in range(0,num):
        db.maccache.insert(mac_cache)


# node_id番のPCWLにコマンドを投げてhtml解析後DB登録
def save_rttmp(ip,node_id,user,pswd):
    data_list[node_id] = []
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
        with urllib.request.urlopen(url=LOGIN_URL, data=b'cmd=/usr/sbin/station_list%20-i%20ath0', timeout=0.5) as page:
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
                    # db.tscache.insert({"th":time_stamp,"node_id":node_id})
                    db.tscache.update({"node_id":node_id},
                                        {"$set": {"th":time_stamp,"node_id":node_id}},
                                        # upsert=True)
                                        upsert=True)
                    first = False
                if time_stamp > ts_th:
                    new_data = {"node_id":node_id,"get_time_no":now,"mac":mac,"rssi":rssi,"dbm":rssi - 95}
                    # data_list.append(new_data)
                    data_list[node_id].append(new_data)
                else :
                    break
            if "Station Count:" in line:
                dbsave_flag = True
    except urllib.error.URLError:
        log_dt = dt_from_14digits_to_iso(str(now))
        db.timeoutlog.insert({"datetime":log_dt, "timeout_ip":ip,"TO_type":"Normal timeout"})
        print("Timeout "+ip)
    except socket.timeout:
        log_dt = dt_from_14digits_to_iso(str(now))
        db.timeoutlog.insert({"datetime":log_dt, "timeout_ip":ip,"TO_type":"Socket timeout"})
        print("Socket Timeout "+ip)
    return data_list[node_id]

def save_function(pcwlip):
    data_list = save_rttmp(pcwlip["ip"],pcwlip["node_id"],user,pswd)
    if len(data_list) > 1:
            db.rttmp.insert(data_list)
            db.rttmp3.insert(data_list)
    # return data_list
    for data in data_list:
        if data["mac"] in tag_list:
            db.trtmp.insert(data)

def multi(pcwliplist):
    p = Pool(8) #プロセス数の選択
    data_list = p.map(save_function, pcwliplist)
