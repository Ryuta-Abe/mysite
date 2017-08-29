# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
# from cms.forms import SensorForm
# from cms.models import Sensor2, Sensor3, initial_db, temp_db, error_db, pr_req
from pfv.models import pr_req, test, pcwlnode, tmpcol, pfvinfo, pfvinfoexperiment, pfvinfoexperiment2, pcwltime, stayinfo, bookmark
# from pfv.convert_nodeid import *
# from pfv.save_pfvinfo import make_pfvinfo
# from pfv.make_pcwltime import make_pcwltime
from mongoengine import *
from pymongo import *
import requests

import json
import math
import datetime
import locale
# dir_ref
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/util/")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/etc/")

from convert_datetime import *
from convert_ip import convert_ip
from pub_web import main

# 今日の日付
d = datetime.datetime.today() # 2014-11-20 19:41:51.011593
dt = datetime.datetime.today() # 2014-11-20 19:41:51.011593
d = str(d.year)+("0"+str(d.month))[-2:]+("0"+str(d.day))[-2:]+("0"+str(d.hour))[-2:]+("0"+str(int(d.minute/5)*5))[-2:] # 201411201940
rt = datetime.datetime.today()

client = MongoClient()
db = client.nm4bd
db.test.create_index([("get_time_no", DESCENDING)])
db.pfvinfo.create_index([("datetime", ASCENDING)])
db.pfvmacinfo.create_index([("datetime", ASCENDING),("mac", ASCENDING)])
db.pfvinfoexperiment.create_index([("datetime", ASCENDING)])
db.stayinfo.create_index([("datetime", ASCENDING)])
db.staymacinfo.create_index([("datetime", ASCENDING),("mac", ASCENDING)])
db.pcwltime.create_index([("datetime", DESCENDING)])
db.pcwlroute.create_index([("query", ASCENDING)])

### データ登録方法 ###
# 1.http://127.0.0.1:8000/pfv/data_list/
# 2.http://127.0.0.1:8000/pfv/aggregate/
# 3.http://127.0.0.1:8000/pfv/analyze/
# 4.http://127.0.0.1:8000/pfv/get_start_end/
# 5.http://127.0.0.1:8000/pfv/pfv_map/

# データリスト画面 http://127.0.0.1:8000/pfv/data_list/
def data_list(request, limit=100, date_time=d):
  dt = int(date_time + "00")

  # データベースから取り出し
  dataset = []
  # t = test.objects(get_time_no__lte=dt).order_by("-get_time_no").limit(int(limit))
  t = db.test.find({"get_time_no":{"$lte":dt}}).sort("get_time_no", DESCENDING).limit(int(limit))
  for data in t:
    data["node_id"] = convert_nodeid(data["node_id"])["node_id"]
    dataset.append(data)
  return render_to_response('pfv/data_list.html',  # 使用するテンプレート
                              {'t': dataset, 'limit':limit, 'year':date_time[0:4],'month':date_time[4:6],
                               'day':date_time[6:8],'hour':date_time[8:10],'minute':date_time[10:12]} )

def analyze_direction(request,mac=":",date_time=d, limit=100):
  from datetime import datetime
  dt = int(date_time + "00")

  # $regex(正規表現) を使うと部分一致の検索が可能
  ag = db.tmpcol.find({"_id.mac":{"$regex":mac},"_id.get_time_no":{"$lte":dt}}).sort("_id.mac").sort("_id.get_time_no",-1).limit(int(limit))
  ana_list = []
  for jdata in ag:
    jdata['id'] = jdata['_id']
    jdata['id']['get_time_no'] = datetime.strptime(str(jdata['id']['get_time_no']), '%Y%m%d%H%M%S')
    jdata['nodelist'] = sorted(jdata['nodelist'], key=lambda x:x["dbm"], reverse=True)
    for list_data in jdata['nodelist']:
      list_data['floor']   = convert_nodeid(list_data['node_id'])['floor']
      list_data['node_id'] = convert_nodeid(list_data['node_id'])['node_id']

    del(jdata['_id'])
    ana_list.append(jdata)
  return render_to_response('pfv/analyze_direction.html',  # 使用するテンプレート
                              {'ag': ana_list, 'mac':mac, 'limit':limit, 'year':date_time[0:4],'month':date_time[4:6],
                               'day':date_time[6:8],'hour':date_time[8:10],'minute':date_time[10:12]}
                            )

# pfvマップ画面 http://localhost:8000/cms/pfv_map/
def pfv_map(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', 'now')
  timerange = int(request.GET.get('timerange', 10))
  mac = request.GET.get('mac', '')
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')

  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  else :
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find({"floor":floor})

  # ブックマーク情報の取り出し
  bookmarks = []
  bookmarks += db.bookmark.find()

  if mac == "": # 全macのビューを表示

    # pfv情報の取り出し
    pfvinfo = []
    pfvinfo += db.pfvinfo.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
    if len(pfvinfo) >= 1:
      for i in range(1,len(pfvinfo)): # timerange内のpfv情報を合成
        for j in range(0,len(pfvinfo[i]["plist"])):
          pfvinfo[i]["plist"][j]["size"] += pfvinfo[i-1]["plist"][j]["size"]
      pfvinfo = pfvinfo[-1]["plist"]
    else :
      # 空のpfvinfo生成
      for i in range(0,len(pcwlnode)):
        for j in range(0,len(pcwlnode)):
          st = pcwlnode[i]["pcwl_id"] # 出発点
          ed = pcwlnode[j]["pcwl_id"] # 到着点
          # iとjが隣接ならば人流0人でpfvinfoに加える
          if ed in pcwlnode[i]["next_id"]:
            pfvinfo.append({"direction":[st,ed],"size":0})

    # 滞留端末情報の取り出し
    stayinfo = []
    stayinfo += db.stayinfo.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
    if len(stayinfo) >= 1:
      for i in range(1,len(stayinfo)):
        for j in range(0,len(stayinfo[i]["plist"])):
          stayinfo[i]["plist"][j]["size"] += stayinfo[i-1]["plist"][j]["size"]
          for new_mac in stayinfo[i]["plist"][j]["mac_list"]:
            if new_mac in stayinfo[i-1]["plist"][j]["mac_list"]:
              stayinfo[i]["plist"][j]["size"] -= 1
            else :
              stayinfo[i-1]["plist"][j]["mac_list"] += [new_mac]
          stayinfo[i]["plist"][j]["mac_list"] = stayinfo[i-1]["plist"][j]["mac_list"]
      stayinfo = stayinfo[-1]["plist"]

    # 滞留端末情報をPCWL情報にひも付け
    _pcwlnode_with_stayinfo = []
    for i in range(0,len(pcwlnode)):
      if len(stayinfo) >= 1:
        size = stayinfo[i]["size"]
      else :
        size = 0
      _pcwlnode_with_stayinfo.append({
        "pcwl_id":pcwlnode[i]["pcwl_id"],
        "pos_x":pcwlnode[i]["pos_x"],
        "pos_y":pcwlnode[i]["pos_y"],
        "size":size
        })

    return render_to_response('pfv/pfv_map.html',  # 使用するテンプレート
                                {'pcwlnode': _pcwlnode_with_stayinfo,'pfvinfo': pfvinfo,'bookmarks':bookmarks,
                                 'language':language,'timerange':timerange,'mac':mac, 'floor':floor,
                                 'year':lt.year,'month':lt.month,'day':lt.day,
                                 'hour':lt.hour,'minute':lt.minute,'second':lt.second}
                                )

  else : # macを絞り込んだビューを表示

    # mac検索条件
    mac_query = [] # 検索するmacのリスト
    mac_num = round(len(mac)/18) # 検索するmac数
    for i in range(0,mac_num):
      mac_query.append(mac[0+i*18:17+i*18].lower())

    # macの色づけ
    color_list = ["blue","red","green","orange","pink"]
    pfvinfo = []
    for i in range(0,len(mac_query)):
      pfvinfo.append({"mac":mac_query[i],"color":color_list[i],"route":[]})

    # pfv情報の取り出し
    tmp_pfvinfo = []
    tmp_pfvinfo += db.pfvmacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

    # 滞留端末情報の取り出し
    tmp_stayinfo = []
    tmp_stayinfo += db.staymacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

    # pfvinfoにroute情報をひも付け
    for t_data in tmp_pfvinfo:
      for p_data in pfvinfo:
        if t_data["mac"] == p_data["mac"]:
          p_data["route"].append(t_data["route"])
    for t_data in tmp_stayinfo:
      for p_data in pfvinfo:
        if t_data["mac"] == p_data["mac"]:
          p_data["route"].append([[t_data["pcwl_id"]]])

    return render_to_response('pfv/pfv_map_mac.html',  # 使用するテンプレート
                                {'pcwlnode': pcwlnode,'pfvinfo': pfvinfo,'bookmarks':bookmarks,
                                 'language':language,'timerange':timerange,'mac':mac, 'floor':floor,
                                 'year':lt.year,'month':lt.month,'day':lt.day,
                                 'hour':lt.hour,'minute':lt.minute,'second':lt.second}
                                )

# pfvマップ用JSON
def pfv_map_json(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', 'now')
  timerange = int(request.GET.get('timerange', 10))
  mac = request.GET.get('mac', '')
  floor = request.GET.get('floor', 'W2-6F')

  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  else :
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  if mac == "": # 全macのビューを表示

    # pfv情報の取り出し
    pfvinfo = []
    pfvinfo += db.pfvinfo.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
    if len(pfvinfo) >= 1:
      for i in range(1,len(pfvinfo)): # timerange内のpfv情報を合成
        for j in range(0,len(pfvinfo[i]["plist"])):
          pfvinfo[i]["plist"][j]["size"] += pfvinfo[i-1]["plist"][j]["size"]
      pfvinfo = pfvinfo[-1]["plist"]
    else :
      pfvinfo += db.pfvinfo.find({"floor":floor}).limit(1)
      pfvinfo = pfvinfo[0]["plist"]
      for j in range(0,len(pfvinfo)):
        pfvinfo[j]["size"] = 0

    # 滞留端末情報の取り出し
    stayinfo = []
    stayinfo += db.stayinfo.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
    if len(stayinfo) >= 1:
      for i in range(1,len(stayinfo)):
        for j in range(0,len(stayinfo[i]["plist"])):
          stayinfo[i]["plist"][j]["size"] += stayinfo[i-1]["plist"][j]["size"]
          for mac in stayinfo[i]["plist"][j]["mac_list"]:
            if mac in stayinfo[i-1]["plist"][j]["mac_list"]:
              stayinfo[i]["plist"][j]["size"] -= 1
            else :
              stayinfo[i-1]["plist"][j]["mac_list"] += [mac]
          stayinfo[i]["plist"][j]["mac_list"] = stayinfo[i-1]["plist"][j]["mac_list"]
      stayinfo = stayinfo[-1]["plist"]

    # 送信するデータセット
    dataset = {"pfvinfo":pfvinfo,"stayinfo":stayinfo}

  else : # macを絞り込んだビューを表示

    # mac検索条件
    mac_query = [] # 検索するmacのリスト
    mac_num = round(len(mac)/18) # 検索するmac数
    for i in range(0,mac_num):
      mac_query.append(mac[0+i*18:17+i*18].lower())

    # macの色づけ
    color_list = ["blue","red","green","orange","pink"]
    pfvinfo = []
    for i in range(0,len(mac_query)):
      pfvinfo.append({"mac":mac_query[i],"color":color_list[i],"route":[]})

    # pfv情報の取り出し
    tmp_pfvinfo = []
    tmp_pfvinfo += db.pfvmacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

    # 滞留端末情報の取り出し
    tmp_stayinfo = []
    tmp_stayinfo += db.staymacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

    # pfvinfoにroute情報をひも付け
    for t_data in tmp_pfvinfo:
      for p_data in pfvinfo:
        if t_data["mac"] == p_data["mac"]:
          p_data["route"].append(t_data["route"])
    for t_data in tmp_stayinfo:
      for p_data in pfvinfo:
        if t_data["mac"] == p_data["mac"]:
          p_data["route"].append([[t_data["pcwl_id"]]])

    # 送信するデータセット
    dataset = {"pfvinfo":pfvinfo}

  return render_json_response(request, dataset) # dataをJSONとして出力

# JSON出力
def render_json_response(request, data, status=None): # response を JSON で返却

  json_str = json.dumps(data, ensure_ascii=False, indent=2)
  callback = request.GET.get('callback')
  if not callback:
      callback = request.REQUEST.get('callback')  # POSTでJSONPの場合
  if callback:
      json_str = "%s(%s)" % (callback, json_str)
      response = HttpResponse(json_str, content_type='application/javascript; charset=UTF-8', status=status)
  else:
      response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
  return response

# pfvグラフ
def pfv_graph(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20150603122130')
  direction = request.GET.get('direction', '2205')
  experiment = int(request.GET.get('experiment', 0))
  language = request.GET.get('language', 'jp')
  mac = request.GET.get('mac', '')
  floor = request.GET.get('floor', 'W2-6F')

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(hours = 2) # 1時間前までのデータを取得

  st = int(direction[0:2])
  ed = int(direction[2:4])

  # mac検索条件
  if mac != "":
    mac_query = [] # 検索するmacのリスト
    mac_num = round(len(mac)/18) # 検索するmac数
    for i in range(0,mac_num):
      mac_query.append(mac[0+i*18:17+i*18]).lower()

  # pfv情報の取り出しとグラフデータ化
  pfvinfo_list = []
  pfvgraph_info = []
  if experiment == 1: # 実験データ
    pfvinfo_list += db.pfvinfoexperiment.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
  elif experiment == 2: # 実験データ2
    pfvinfo_list += db.pfvinfoexperiment2.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
  elif mac == "": # すべてのmacの取り出し
    pfvinfo_list += db.pfvinfo.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
  else : # 特定のmacを抽出
    pfvinfo_list += db.pfvmacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor}).sort("datetime", ASCENDING)
  if len(pfvinfo_list) >= 1:
    for i in range(0,len(pfvinfo_list[0]["plist"])):
      if (pfvinfo_list[0]["plist"][i]["direction"][0] == st) and (pfvinfo_list[0]["plist"][i]["direction"][1] == ed):
        num = i
    for pfvinfo in pfvinfo_list:
      pfvgraph_info.append({"datetime":pfvinfo["datetime"],"size":pfvinfo["plist"][num]["size"]})

  return render_to_response('pfv/pfv_graph.html',  # 使用するテンプレート
                              {'pfvgraph_info': pfvgraph_info, 'experiment':experiment
                              ,'start_node':st, 'end_node':ed, 'language':language, 'mac':mac
                              ,'year':lt.year,'month':lt.month,'day':lt.day
                              ,'hour':lt.hour,'minute':lt.minute,'second':lt.second}
                              )

# stayグラフ
def stay_graph(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20150603122130')
  node = int(request.GET.get('node', 1))
  language = request.GET.get('language', 'jp')
  mac = request.GET.get('mac', '')
  floor = request.GET.get('floor', 'W2-6F')

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(hours = 2) # 1時間前までのデータを取得

  # mac検索条件
  if mac != "":
    mac_query = [] # 検索するmacのリスト
    mac_num = round(len(mac)/18) # 検索するmac数
    for i in range(0,mac_num):
      mac_query.append(mac[0+i*18:17+i*18])

  # 滞留端末情報の取り出しとグラフデータ化
  stayinfo_list = []
  staygraph_info = []
  if mac == "": # すべてのmacの取り出し
    stayinfo_list += db.stayinfo.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
  else : # 特定のmacを抽出
    stayinfo_list += db.staymacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor}).sort("datetime", ASCENDING)
  if len(stayinfo_list) >= 1:
    for i in range(0,len(stayinfo_list[0]["plist"])):
      if stayinfo_list[0]["plist"][i]["pcwl_id"] == node:
        num = i
    for stayinfo in stayinfo_list:
      staygraph_info.append({"datetime":stayinfo["datetime"],"size":stayinfo["plist"][num]["size"]})

  return render_to_response('pfv/stay_graph.html',  # 使用するテンプレート
                              {'staygraph_info': staygraph_info, 'node':int(node)
                              , 'language':language, 'mac':mac
                              ,'year':lt.year,'month':lt.month,'day':lt.day
                              ,'hour':lt.hour,'minute':lt.minute,'second':lt.second}
                              )

#時間変換用の関数(iso形式 --> 20150603122130(str) )
def dt_from_iso_to_str14(dt):

  dt = str(dt.year)+("0"+str(dt.month))[-2:]+("0"+str(dt.day))[-2:]+("0"+str(dt.hour))[-2:]+("0"+str(dt.minute))[-2:]+("00"+str(dt.second))[-2:]
  return dt

def mac_trace(request):
  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', 'now')
  mac = request.GET.get('mac', '')
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')

  timerange = 5
  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  else:
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  # pcwl情報の取り出し
  pcwlnode = []
  # pcwlnode += db.pcwlnode.find()
  pcwlnode += db.pcwlnode.find({"floor":floor})

  # mac検索条件
  if mac != "":
    mac_query = [] # 検索するmacのリスト
    mac_num = round(len(mac)/18) # 検索するmac数
    for i in range(0,mac_num):
      mac_query.append(mac[0+i*18:17+i*18])

  dataset = []
  if mac == "":
    t = []
  else :
    t = db.tmpcol_backup.find({"_id.get_time_no":{"$gt":gt, "$lte":lt},"_id.mac":{"$in":mac_query}}).sort("_id.get_time_no", DESCENDING)

  for data in t:
    if convert_ip(data["nodelist"][0]["ip"])["floor"] == floor:
      for i in range(0,len(data["nodelist"])):
        data["nodelist"][i]["node_id"] = convert_ip(data["nodelist"][i]["ip"])["pcwl_id"]
      dataset.append(data)

  # ブックマーク情報の取り出し
  bookmarks = []
  bookmarks += db.tagbookmark.find()

  #データをdbmでソート
  if dataset != []:
    for i in range(0,len(dataset)):
      dataset[i]['nodelist'] = sorted(dataset[i]['nodelist'], key=lambda x:x["dbm"], reverse=True)

  #dbmの上位3つだけを取り出す
  for data in dataset:
    for i in range(0,len(data["nodelist"])):
      if i < 3:
        pass
      else:
        del data["nodelist"][3]

  #rssiをPCWL情報にひも付け
  _pcwlnode_with_rssi = []
  for i in range(0,len(pcwlnode)):
    pcwlnode[i]["rssi"] = 0
    for data in dataset:
      for j in range(0,len(data["nodelist"])):
        if pcwlnode[i]["pcwl_id"] == data["nodelist"][j]["node_id"]:
          pcwlnode[i]["rssi"] += data["nodelist"][j]["dbm"]
    _pcwlnode_with_rssi.append({
      "pcwl_id":pcwlnode[i]["pcwl_id"],
      "pos_x":pcwlnode[i]["pos_x"],
      "pos_y":pcwlnode[i]["pos_y"],
      "rssi":pcwlnode[i]["rssi"]
      })

  return render_to_response('pfv/mac_trace.html',  # 使用するテンプレート
                              # {'floor':floor,'mac_data':mac_data,'pcwlnode': _pcwlnode_with_rssi,'bookmarks':bookmarks,
                              {'floor':floor,'pcwlnode': _pcwlnode_with_rssi,'bookmarks':bookmarks,
                               'language':language,'mac':mac,
                               'year':lt.year,'month':lt.month,'day':lt.day,
                               'hour':lt.hour,'minute':lt.minute,'second':lt.second}
                              )

# mac_trace用JSON
def mac_trace_json(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', 'now')
  mac = request.GET.get('mac', '')
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')

  timerange = 5
  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  else:
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find({"floor":floor})

  # mac検索条件
  if mac != "":
    mac_query = [] # 検索するmacのリスト
    mac_num = round(len(mac)/18) # 検索するmac数
    for i in range(0,mac_num):
      mac_query.append(mac[0+i*18:17+i*18])

  # 指定時間のデータの取り出し
  dataset = []
  if mac == "":
    t = []
  else :
    t = db.tmpcol_backup.find({"_id.get_time_no":{"$gt":gt, "$lte":lt},"_id.mac":{"$in":mac_query}}).sort("_id.get_time_no", DESCENDING)

  for data in t:
    if convert_ip(data["nodelist"][0]["ip"])["floor"] == floor:
      for i in range(0,len(data["nodelist"])):
        data["nodelist"][i]["node_id"] = convert_ip(data["nodelist"][i]["ip"])["pcwl_id"]
      dataset.append(data)

  #データをdbmでソート
  if dataset != []:
    for i in range(0,len(dataset)):
      dataset[i]['nodelist'] = sorted(dataset[i]['nodelist'], key=lambda x:x["dbm"], reverse=True)

  #dbmの上位3つだけを取り出す
  for data in dataset:
    for i in range(0,len(data["nodelist"])):
      if i < 3:
        pass
      else:
        del data["nodelist"][3]

  #rssiをPCWL情報にひも付け
  _pcwlnode_with_rssi = []
  for i in range(0,len(pcwlnode)):
    pcwlnode[i]["rssi"] = 0
    for data in dataset:
      for j in range(0,len(data["nodelist"])):
        if pcwlnode[i]["pcwl_id"] == data["nodelist"][j]["node_id"]:
          pcwlnode[i]["rssi"] += data["nodelist"][j]["dbm"]
    _pcwlnode_with_rssi.append({
      "pcwl_id":pcwlnode[i]["pcwl_id"],
      "pos_x":pcwlnode[i]["pos_x"],
      "pos_y":pcwlnode[i]["pos_y"],
      "rssi":pcwlnode[i]["rssi"]
      })

  info = {"_pcwlnode_with_rssi":_pcwlnode_with_rssi}
  return render_json_response(request, info) # dataをJSONとして出力

  # pfvマップ画面 http://localhost:8000/pfv/pfv_heatmap/
def pfv_heatmap(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20150603122130')
  timerange = int(request.GET.get('timerange', 10))
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  #heatmapinfoからの取り出し
  heatmapinfo = []
  heatmapinfo += db.heatmapinfo.find({"datetime":{"$gt":gt, "$lte":lt}}).sort("datetime", ASCENDING)

  coordinate_size = []
  for info in heatmapinfo:
    tmp_coordinatesize = []
    for cs in info["coordinate_size"]:
      tmp_coordinatesize.append(cs)
    coordinate_size.append(tmp_coordinatesize)

  if len(coordinate_size) > 1:
    for i in range(1,len(coordinate_size)):
      for j in range (0,252):
        coordinate_size[0][j]["size"] += coordinate_size[i][j]["size"]
  coordinate_size = coordinate_size[0]

  return render_to_response('pfv/pfv_heatmap.html',  # 使用するテンプレート
                              {'floor':floor,'coordinate_size':coordinate_size,'language':language,'timerange':timerange,
                               'year':lt.year,'month':lt.month,'day':lt.day,
                               'hour':lt.hour,'minute':lt.minute,'second':lt.second}
                              )

def pfv_heatmap_json(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20150603122130')
  timerange = int(request.GET.get('timerange', 10))
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')

  lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  #heatmapinfoからの取り出し
  heatmapinfo = []
  heatmapinfo += db.heatmapinfo.find({"datetime":{"$gt":gt, "$lte":lt}}).sort("datetime", ASCENDING)

  coordinate_size = []
  for info in heatmapinfo:
    tmp_coordinatesize = []
    for cs in info["coordinate_size"]:
      tmp_coordinatesize.append(cs)
    coordinate_size.append(tmp_coordinatesize)

  if len(coordinate_size) > 1:
    for i in range(1,len(coordinate_size)):
      for j in range (0,252):
        coordinate_size[0][j]["size"] += coordinate_size[i][j]["size"]
  coordinate_size = coordinate_size[0]

  info = {"coordinate_size":coordinate_size}
  return render_json_response(request, info) # dataをJSONとして出力


def count_result(request):
  dt = str(20160307160000)
  mac = ""
  floor = "kaiyo"

  # データベースから取り出し
  nodeset = []
  nodedir_set = []
  all_count_dict = {}
  all_staycount_dict = {}
  nodelist = db.pcwlnode.find({"floor":"kaiyo"}).sort("pcwl_id", ASCENDING)
  for data in nodelist:
    st_id = data["pcwl_id"]
    for ed_id in data["next_id"]:
      st_id = ("0"+str(st_id))[-2:]
      ed_id = ("0"+str(ed_id))[-2:]
      direction_id = st_id + ed_id
      nodedir_set.append(direction_id)
      all_count_dict.update({direction_id:0})
    nodeset.append(st_id)
    all_staycount_dict.update({int(data["pcwl_id"]):0})

  # mac検索条件
  if mac != "":
    mac_query = [] # 検索するmacのリスト
    mac_num = round(len(mac)/18) # 検索するmac数
    for i in range(0,mac_num):
      mac_query.append(mac[0+i*18:17+i*18]).lower()

  ############
  # dataset = []
  # t = db.test.find({"get_time_no":{"$lte":dt}}).sort("get_time_no", DESCENDING).limit(int(limit))
  # for data in t:
  #   data["node_id"] = convert_nodeid(data["node_id"])["node_id"]
  #   dataset.append(data)

  # # urlからクエリの取り出し
  # lt = dt_from_14digits_to_iso(date_time)
  # gt = lt - datetime.timedelta(hours = 2) # 1時間前までのデータを取得

  # st = int(direction[0:2])
  # ed = int(direction[2:4])
  ############

  dataset = []
  sdataset = []
  lt = dt_from_14digits_to_iso(dt)
  interval = datetime.timedelta(minutes = 10)
  all_countlist = []
  all_staycountlist = []
  time_cnt = 0

  while (datetime.datetime(2016, 3, 7, 13, 00, 00) < lt):
    gt = lt - interval

    # # pfv情報の取り出しとグラフデータ化
    pfvinfo_list = []
    stayinfo_list = []
    if mac == "": # すべてのmacの取り出し
      pfvinfo_list += db.pfvinfo.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
      stayinfo_list += db.stayinfo.find({"datetime":{"$gt":gt, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
    else : # 特定のmacを抽出
      pfvinfo_list += db.pfvmacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor}).sort("datetime", ASCENDING)
      stayinfo_list += db.staymacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor}).sort("datetime", ASCENDING)

    # print(pfvinfo_list)
    num = 0
    count_list = []
    cnt = 0
    if len(pfvinfo_list) >= 1:
      for direction in nodedir_set:
        st = int(direction[0:2])
        ed = int(direction[2:4])
        count_info = []

        for i in range(0,len(pfvinfo_list[0]["plist"])):
          if (pfvinfo_list[0]["plist"][i]["direction"][0] == st) and (pfvinfo_list[0]["plist"][i]["direction"][1] == ed):
            num = i
        for pfvinfo in pfvinfo_list:
          count_info.append({"datetime":pfvinfo["datetime"],"size":pfvinfo["plist"][num]["size"]})

        total_size = 0
        cnt = 0
        for data in count_info:
          total_size += data["size"]
          cnt += 1
        if cnt == 0:
          ave = 0
        else:
          ave = round(100*total_size/cnt)/100
        count_list.append(ave)
        total_ave = all_count_dict[direction] + ave
        all_count_dict.update({direction:total_ave})
        # count_list.append({"total":round(total_size), "count":cnt, "ave":ave})
    dataset.append({"datetime":gt, "count_list":count_list})

    s_num = 0
    staycount_list = []
    cnt = 0
    if len(stayinfo_list) >= 1:
      for node in nodeset:
        node = int(node)
        staycount_info = []
        for i in range(0,len(stayinfo_list[0]["plist"])):
          if stayinfo_list[0]["plist"][i]["pcwl_id"] == node:
            s_num = i
        for stayinfo in stayinfo_list:
          staycount_info.append({"datetime":stayinfo["datetime"],"size":stayinfo["plist"][s_num]["size"]})

        print("s_num="+str(s_num))
        total_size = 0
        cnt = 0
        for data in staycount_info:
          total_size += data["size"]
          cnt += 1
        if cnt == 0:
          ave = 0
        else:
          ave = round(100*total_size/cnt)/100
        staycount_list.append(ave)
        total_ave = all_staycount_dict[node] + ave
        all_staycount_dict.update({node:total_ave})
        # count_list.append({"total":round(total_size), "count":cnt, "ave":ave})
    sdataset.append({"datetime":gt, "staycount_list":staycount_list})

    print(lt)
    lt = gt
    time_cnt += 1

  for direction in nodedir_set:
    tmp = round(100*all_count_dict[direction]/time_cnt)/100
    all_countlist.append(tmp)
  dataset.append({"datetime":datetime.datetime(2016,3,7,0,0,0), "count_list":all_countlist})

  for node in nodeset:
    tmp = round(100*all_staycount_dict[int(node)]/time_cnt)/100
    all_staycountlist.append(tmp)
  sdataset.append({"datetime":datetime.datetime(2016,3,7,0,0,0), "staycount_list":all_staycountlist})

  return render_to_response('pfv/count_result.html',  # 使用するテンプレート
                              {'t': dataset, 'nodedir_set':nodedir_set, 'sdataset':sdataset,
                               'nodeset':nodeset,
                              # 'limit':limit, 'year':date_time[0:4],'month':date_time[4:6],
                              #  'day':date_time[6:8],'hour':date_time[8:10],'minute':date_time[10:12]
                               }
                               )

def tag_track_map(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', 'now')
  timerange = int(request.GET.get('timerange', 5))
  mac = request.GET.get('mac', '00:11:81:10:01:1b,00:11:81:10:01:00,00:11:81:10:01:0d,00:11:81:10:01:0c,00:11:81:10:01:0e,00:11:81:10:01:3d')
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')

  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  else :
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  gt_tag = lt - datetime.timedelta(seconds = 5) # 5秒前までのデータを取得
  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find({"floor":floor})

  # timeout情報の取り出し
  timeout = []
  timeout += db.timeoutlog.find({"datetime":{"$gt":gt_tag, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)

  for i in pcwlnode:
    i["state"] = "default"
    for j in timeout:
      if j["pcwl_id"] == i["pcwl_id"]:
        i["state"] = "timeout"
        break

  # ブックマーク情報の取り出し
  tagbookmarks = []
  tagbookmarks += db.tagbookmark.find()

  # mac検索条件
  mac_query = [] # 検索するmacのリスト
  mac_num = round(len(mac)/18) # 検索するmac数
  for i in range(0,mac_num):
    mac_query.append(mac[0+i*18:17+i*18].lower())

  # macの色づけ
  color_list = ["blue","red","limegreen","orange","magenta","turquoise"]
  pfvinfo = []
  for i in range(0,len(mac_query)):
    pfvinfo.append({"mac":mac_query[i],"color":color_list[i],"route":[],"floor":"×"})

  # pfv情報の取り出し
  tmp_pfvinfo = []
  tmp_pfvinfo += db.pfvmacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

  # 滞留端末情報の取り出し
  tmp_stayinfo = []
  tmp_stayinfo += db.staymacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

  # pfvinfoにroute情報をひも付け
  for t_data in tmp_pfvinfo:
    for p_data in pfvinfo:
      if t_data["mac"] == p_data["mac"]:
        p_data["route"].append(t_data["route"])
  for t_data in tmp_stayinfo:
    for p_data in pfvinfo:
      if t_data["mac"] == p_data["mac"]:
        p_data["route"].append([[t_data["pcwl_id"]]])

  #pfvinfoに現在のfloor情報を紐付け
  floor_list = ["W2-6F","W2-7F","W2-8F","W2-9F"]
  for i in pfvinfo:
    for j in floor_list:
      tmp_count = []
      tmp_count += db.pfvmacinfo.find({"datetime":{"$gt":gt_tag, "$lte":lt},"mac":i["mac"], "floor":j},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)
      tmp_count += db.staymacinfo.find({"datetime":{"$gt":gt_tag, "$lte":lt},"mac":i["mac"], "floor":j},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)
      if len(tmp_count) >= 1:
        i["floor"] = j
        break



  return render_to_response('pfv/tag_track_map.html',  # 使用するテンプレート
                              {'pcwlnode': pcwlnode,'pfvinfo': pfvinfo,'bookmarks':tagbookmarks,
                               'language':language,'timerange':timerange,'mac':mac, 'floor':floor,
                               'year':lt.year,'month':lt.month,'day':lt.day,
                               'hour':lt.hour,'minute':lt.minute,'second':lt.second}
                              )

def tag_track_map_json(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', 'now')
  timerange = int(request.GET.get('timerange', 5))
  mac = request.GET.get('mac', '00:11:81:10:01:1b,00:11:81:10:01:00,00:11:81:10:01:0d,00:11:81:10:01:0c,00:11:81:10:01:0e,00:11:81:10:01:3d')
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')
  selectnode = request.GET.get("selectnode", "")
  realtime = request.GET.get("realtime", "false")

  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  elif realtime == "true":
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 10) # 現在時刻の5秒前を表示時間に
  else :
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得


  gt_tag = lt - datetime.timedelta(seconds = 5) # 5秒前までのデータを取得
  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find({"floor":floor})
  # timeout情報の取り出し
  timeout = []
  timeout += db.timeoutlog.find({"datetime":{"$gt":gt_tag, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
  for i in pcwlnode:
    del i["_id"]
    i["state"] = "default"
    for j in timeout:
      if j["pcwl_id"] == i["pcwl_id"]:
        i["state"] = "timeout"
        break

  # mac検索条件
  mac_query = [] # 検索するmacのリスト
  mac_num = round(len(mac)/18) # 検索するmac数
  for i in range(0,mac_num):
    mac_query.append(mac[0+i*18:17+i*18].lower())

# 選択ノードよりmqttトリガー
  if len(selectnode) != 0:
    selectnode = list(map(int, selectnode.split(",")))
    light_list = []
    for tag in range(3):
      if (db.staymacinfo.find({"mac":mac_query[tag], "datetime":{"$gt":gt_tag, "$lte":lt}, "pcwl_id": {"$in":selectnode}}).count()!=0):
        light_list.append(True)
      elif (db.pfvmacinfo.find({"mac":mac_query[tag], "datetime":{"$gt":gt_tag, "$lte":lt}, "floor": floor}).count()!=0):
        flow_list = []
        flow_list += db.pfvmacinfo.find({"mac":mac_query[tag], "datetime":{"$gt":gt_tag, "$lte":lt}, "floor": floor})
        light_list.append(False)
        for i in flow_list[0]["route"]:
          if i[0] in selectnode:
            light_list.pop()
            light_list.append(True)
            break
          elif i[1] in selectnode:
            light_list.pop()
            light_list.append(True)
            break
      else:
        light_list.append(False)
    main(light_list)

  # macの色づけ
  color_list = ["blue","red","limegreen","orange","magenta","turquoise"]
  pfvinfo = []
  for i in range(0,len(mac_query)):
    pfvinfo.append({"mac":mac_query[i],"color":color_list[i],"route":[],"floor":"×"})

  # pfv情報の取り出し
  tmp_pfvinfo = []
  tmp_pfvinfo += db.pfvmacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

  # 滞留端末情報の取り出し
  tmp_stayinfo = []
  tmp_stayinfo += db.staymacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

  # pfvinfoにroute情報をひも付け
  for t_data in tmp_pfvinfo:
    for p_data in pfvinfo:
      if t_data["mac"] == p_data["mac"]:
        p_data["route"].append(t_data["route"])
  for t_data in tmp_stayinfo:
    for p_data in pfvinfo:
      if t_data["mac"] == p_data["mac"]:
        p_data["route"].append([[t_data["pcwl_id"]]])

#pfvinfoに現在のfloor情報を紐付け
  floor_list = ["W2-6F","W2-7F","W2-8F","W2-9F"]
  for i in pfvinfo:
    for j in floor_list:
      tmp_count = []
      tmp_count += db.pfvmacinfo.find({"datetime":{"$gt":gt_tag, "$lte":lt},"mac":i["mac"], "floor":j},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)
      tmp_count += db.staymacinfo.find({"datetime":{"$gt":gt_tag, "$lte":lt},"mac":i["mac"], "floor":j},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)
      if len(tmp_count) >= 1:
        i["floor"] = j
        break

  #realtime使用時のみ必要になる
  realtime = {'year':lt.year,'month':lt.month,'day':lt.day,'hour':lt.hour,'minute':lt.minute,'second':lt.second}

  # 送信するデータセット
  dataset = {"pfvinfo":pfvinfo,"pcwlnode":pcwlnode,"realtime":realtime}
  # dataset = {"pfvinfo":pfvinfo}

  return render_json_response(request, dataset) # dataをJSONとして出力

#座標チェック用
def tag_position_check(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', 'now')
  timerange = int(request.GET.get('timerange', 5))
  mac = request.GET.get('mac', '00:11:81:10:01:1b,00:11:81:10:01:00,00:11:81:10:01:0d,00:11:81:10:01:0c,00:11:81:10:01:0e,00:11:81:10:01:3d')
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-7F')

  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  else :
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  gt_tag = lt - datetime.timedelta(seconds = 5) # 5秒前までのデータを取得
  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find({"floor":floor})

  # timeout情報の取り出し
  timeout = []
  timeout += db.timeoutlog.find({"datetime":{"$gt":gt_tag, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)

  for i in pcwlnode:
    i["state"] = "default"
    for j in timeout:
      if j["pcwl_id"] == i["pcwl_id"]:
        i["state"] = "timeout"
        break

  # ブックマーク情報の取り出し
  tagbookmarks = []
  tagbookmarks += db.tagbookmark.find()

  # mac検索条件
  mac_query = [] # 検索するmacのリスト
  mac_num = round(len(mac)/18) # 検索するmac数
  for i in range(0,mac_num):
    mac_query.append(mac[0+i*18:17+i*18].lower())

  # macの色づけ
  color_list = ["blue","red","limegreen","orange","magenta","turquoise"]
  pfvinfo = []
  for i in range(0,len(mac_query)):
    pfvinfo.append({"mac":mac_query[i],"color":color_list[i],"route":[],"floor":"×"})

  # pfv情報の取り出し
  tmp_pfvinfo = []
  tmp_pfvinfo += db.pfvmacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

  # 滞留端末情報の取り出し
  tmp_stayinfo = []
  tmp_stayinfo += db.staymacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

  # pfvinfoにroute情報をひも付け
  for t_data in tmp_pfvinfo:
    for p_data in pfvinfo:
      if t_data["mac"] == p_data["mac"]:
        p_data["route"].append(t_data["route"])
  for t_data in tmp_stayinfo:
    for p_data in pfvinfo:
      if t_data["mac"] == p_data["mac"]:
        p_data["route"].append([[t_data["pcwl_id"]]])

  #pfvinfoに現在のfloor情報を紐付け
  floor_list = ["W2-6F","W2-7F","W2-8F","W2-9F"]
  for i in pfvinfo:
    for j in floor_list:
      tmp_count = []
      tmp_count += db.pfvmacinfo.find({"datetime":{"$gt":gt_tag, "$lte":lt},"mac":i["mac"], "floor":j},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)
      tmp_count += db.staymacinfo.find({"datetime":{"$gt":gt_tag, "$lte":lt},"mac":i["mac"], "floor":j},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)
      if len(tmp_count) >= 1:
        i["floor"] = j
        break

  #解析位置のデータ取り出し
  analy_coord = []
  analy_coord += db.analy_coord.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor}).sort("datetime", ASCENDING)
  examine_coord = []
  examine_coord += db.examine_route.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor}).sort("datetime", ASCENDING)
  if len(analy_coord) != 0:
    for i in range(len(analy_coord)):
      del analy_coord[i]["_id"]
      del analy_coord[i]["datetime"]
  if len(examine_coord) != 0:
    for i in range(len(examine_coord)):
      del examine_coord[i]["_id"]
      del examine_coord[i]["datetime"]

  return render_to_response('pfv/tag_position_check.html',  # 使用するテンプレート
                              {'pcwlnode': pcwlnode,'pfvinfo': pfvinfo,'bookmarks':tagbookmarks,
                               'language':language,'timerange':timerange,'mac':mac, 'floor':floor,
                               'year':lt.year,'month':lt.month,'day':lt.day,
                               'hour':lt.hour,'minute':lt.minute,'second':lt.second,
                               'analy_coord':analy_coord, 'examine_coord':examine_coord}
                              )

def tag_position_check_json(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', 'now')
  timerange = int(request.GET.get('timerange', 5))
  mac = request.GET.get('mac', '00:11:81:10:01:1b,00:11:81:10:01:00,00:11:81:10:01:0d,00:11:81:10:01:0c,00:11:81:10:01:0e,00:11:81:10:01:3d')
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')
  selectnode = request.GET.get("selectnode", "")

  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  else :
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  gt_tag = lt - datetime.timedelta(seconds = 5) # 5秒前までのデータを取得
  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find({"floor":floor})
  # timeout情報の取り出し
  timeout = []
  timeout += db.timeoutlog.find({"datetime":{"$gt":gt_tag, "$lte":lt}, "floor":floor}).sort("datetime", ASCENDING)
  for i in pcwlnode:
    del i["_id"]
    i["state"] = "default"
    for j in timeout:
      if j["pcwl_id"] == i["pcwl_id"]:
        i["state"] = "timeout"
        break

  # mac検索条件
  mac_query = [] # 検索するmacのリスト
  mac_num = round(len(mac)/18) # 検索するmac数
  for i in range(0,mac_num):
    mac_query.append(mac[0+i*18:17+i*18].lower())

  # macの色づけ
  color_list = ["blue","red","limegreen","orange","magenta","turquoise"]
  pfvinfo = []
  for i in range(0,len(mac_query)):
    pfvinfo.append({"mac":mac_query[i],"color":color_list[i],"route":[],"floor":"×"})

  # pfv情報の取り出し
  tmp_pfvinfo = []
  tmp_pfvinfo += db.pfvmacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

  # 滞留端末情報の取り出し
  tmp_stayinfo = []
  tmp_stayinfo += db.staymacinfo.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)

  # pfvinfoにroute情報をひも付け
  for t_data in tmp_pfvinfo:
    for p_data in pfvinfo:
      if t_data["mac"] == p_data["mac"]:
        p_data["route"].append(t_data["route"])
  for t_data in tmp_stayinfo:
    for p_data in pfvinfo:
      if t_data["mac"] == p_data["mac"]:
        p_data["route"].append([[t_data["pcwl_id"]]])

  #pfvinfoに現在のfloor情報を紐付け
  floor_list = ["W2-6F","W2-7F","W2-8F","W2-9F"]
  for i in pfvinfo:
    for j in floor_list:
      tmp_count = []
      tmp_count += db.pfvmacinfo.find({"datetime":{"$gt":gt_tag, "$lte":lt},"mac":i["mac"], "floor":j},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)
      tmp_count += db.staymacinfo.find({"datetime":{"$gt":gt_tag, "$lte":lt},"mac":i["mac"], "floor":j},{"datetime":0,"floor":0,"_id":0}).sort("datetime", ASCENDING)
      if len(tmp_count) >= 1:
        i["floor"] = j
        break

  #解析位置のデータ取り出し
  analy_coord = []
  analy_coord += db.analy_coord.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor}).sort("datetime", ASCENDING)
  examine_coord = []
  examine_coord += db.examine_route.find({"datetime":{"$gt":gt, "$lte":lt},"mac":{"$in":mac_query}, "floor":floor}).sort("datetime", ASCENDING)
  if len(analy_coord) != 0:
    for i in range(len(analy_coord)):
      del analy_coord[i]["_id"]
      del analy_coord[i]["datetime"]
  if len(examine_coord) != 0:
    for i in range(len(examine_coord)):
      del examine_coord[i]["_id"]
      del examine_coord[i]["datetime"]


  # 送信するデータセット
  dataset = {"pfvinfo":pfvinfo,"pcwlnode":pcwlnode, 'analy_coord':analy_coord, 'examine_coord':examine_coord}
  # dataset = {"pfvinfo":pfvinfo}

  return render_json_response(request, dataset) # dataをJSONとして出力

#群測位用マップ
def crowd_map(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', '20170621060000')
  timerange = int(request.GET.get('timerange', 5))
  mac = request.GET.get('mac', '')
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')

  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  else :
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  # 指定期間の時刻のリストを作成
  time_list = []
  for i in range(1,int(timerange/5)):
    time_list.append(gt + datetime.timedelta(seconds = i*5))
  time_list.append(lt)

  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find({"floor":floor},{"_id":0})

  pfvinfo = [] # 空のpfvinfo生成
  exist_mac = [] #出現中のmacを一時保存
  route_info =[] #経路ごとに格経路パターンを格納
  for i in range(0,len(pcwlnode)):
    for j in range(0,len(pcwlnode)):
      st = pcwlnode[i]["pcwl_id"] # 出発点
      ed = pcwlnode[j]["pcwl_id"] # 到着点
      # iとjが隣接ならば人流0人でpfvinfoに加える
      if ed in pcwlnode[i]["next_id"]:
        pfvinfo.append({"direction":[st,ed],"size":0})

  for i in range(len(pcwlnode)):
    pcwlnode[i]["mac_len"] = []
    pcwlnode[i]["size"] = 0

  # 時刻ごとに経路情報を作成
  for time in time_list:
    # pfv情報の取り出し
    tmp_pfvinfo = []
    tmp_pfvinfo += db.pfvinfo.find({"datetime":time, "floor":floor}).sort("datetime", ASCENDING)
    pfvmacinfo = []
    pfvmacinfo += db.pfvmacinfo.find({"datetime":time, "floor":floor}).sort("datetime", ASCENDING)
    # 滞留端末情報の取り出し
    stayinfo = []
    stayinfo += db.stayinfo.find({"datetime":time, "floor":floor}).sort("datetime", ASCENDING)
    staymacinfo = []
    staymacinfo += db.staymacinfo.find({"datetime":time, "floor":floor}).sort("datetime", ASCENDING)
    # 全体のデータを作成===========================================================
    if len(tmp_pfvinfo) >= 1:
      for i in range(0,len(tmp_pfvinfo[0]["plist"])):
        pfvinfo[i]["size"] += tmp_pfvinfo[0]["plist"][i]["size"]
    if len(stayinfo) >= 1:
      for i in range(0,len(stayinfo[0]["plist"])):
        pcwlnode[i]["size"] += stayinfo[0]["plist"][i]["size"]
        for new_mac in stayinfo[0]["plist"][i]["mac_list"]:
          if new_mac in pcwlnode[i]["mac_len"]:
            pass
          else :
            pcwlnode[i]["mac_len"] += [new_mac]
    # ===========================================================================

    # 経路情報を作成===============================================================
    # tmp_mac = []
    # for i in pfvmacinfo[0]:
    #   if i["mac"] in exist_mac:
    #     if route_info[i["mac"]]

      # stayinfo = stayinfo[-1]["plist"]
      # for i in range(len(pcwlnode)):
      #   pcwlnode[i]["mac_len"] = len(stayinfo[i]["mac_list"])
      #   pcwlnode[i]["size"] = stayinfo[i]["size"]
      #   pcwlnode[i]["color"] = "red"

  # 最大経路通過数・最多経路順を生成
  max_pfv = 0
  keyfunc_pfv = lambda x:x["size"]
  tmp_sort_pfv = sorted(pfvinfo,key=keyfunc_pfv)
  sort_pfv = []
  for i in tmp_sort_pfv:
    if i["size"] != 0:
      if i["size"] == max_pfv:
        sort_pfv[0]["direction"].append(i["direction"])
      else:
        sort_pfv.insert(0,{"size":i["size"],"direction":[i["direction"]]})
        max_pfv = i["size"]
  if len(sort_pfv) != 0:
    min_pfv = sort_pfv[-1]["size"]
  else:
    min_pfv = 0
  rank_pfv = sort_pfv[:3] #上位3位まで取り出し

  # 滞留回数・端末数の最大･最小および順序を作成
  for i in range(len(pcwlnode)):
    pcwlnode[i]["mac_len"] = len(pcwlnode[i]["mac_len"])
  keyfunc_node = lambda x:x["size"]
  keyfunc_mac = lambda x:x["mac_len"]
  tmp_sort_node = sorted(pcwlnode,key=keyfunc_node)
  tmp_sort_mac = sorted(pcwlnode,key=keyfunc_mac)
  sort_node =[]
  sort_mac = []
  max_node = 0
  max_mac = 0
  for i in tmp_sort_node:
    if i["size"] != 0:
      if max_node == i["size"]:
        sort_node[0]["pcwl_id"].append(i["pcwl_id"])
      else:
        sort_node.insert(0,{"size":i["size"],"pcwl_id":[i["pcwl_id"]]})
        max_node = i["size"]
  if len(sort_node) != 0:
    min_node = sort_node[-1]["size"]
  else:
    min_node = 0
  rank_node = sort_node[:3] #上位3位まで取り出し
  for i in tmp_sort_mac:
    if i["mac_len"] != 0:
      if max_mac == i["mac_len"]:
        sort_mac[0]["pcwl_id"].append(i["pcwl_id"])
      else:
        sort_mac.insert(0,{"mac_len":i["mac_len"],"pcwl_id":[i["pcwl_id"]]})
        max_mac = i["mac_len"]
  if len(sort_mac) != 0:
    min_mac = sort_mac[-1]["mac_len"]
  else:
    min_mac = 0
  rank_mac = sort_mac[:3] #上位3位まで取り出し
  ap_data = {"max_node":max_node,"min_node":min_node,"max_mac":max_mac,"min_mac":min_mac}
  flow_data ={"max_pfv":max_pfv,"min_pfv":min_pfv}

  return render_to_response('pfv/crowd_map.html',  # 使用するテンプレート
                              {'pcwlnode': pcwlnode,'pfvinfo': pfvinfo,
                               'language':language,'timerange':timerange,'floor':floor,
                               'year':lt.year,'month':lt.month,'day':lt.day,
                               'hour':lt.hour,'minute':lt.minute,'second':lt.second,"flow_data":flow_data,"ap_data":ap_data,"rank_pfv":rank_pfv,"rank_node":rank_node,"rank_mac":rank_mac
                               }
                              )

def crowd_map_json(request):

  # urlからクエリの取り出し
  date_time = request.GET.get('datetime', 'now')
  timerange = int(request.GET.get('timerange', 5))
  mac = request.GET.get('mac', '')
  language = request.GET.get('language', 'jp')
  floor = request.GET.get('floor', 'W2-6F')
  selectnode = request.GET.get("selectnode", "")
  realtime = request.GET.get("realtime", "false")

  if date_time == 'now':
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 20) # 現在時刻の20秒前をデフォルト表示時間に
  elif realtime == "true":
    lt = datetime.datetime.today() - datetime.timedelta(seconds = 10) # 現在時刻の5秒前を表示時間に
  else :
    lt = dt_from_14digits_to_iso(date_time)
  gt = lt - datetime.timedelta(seconds = timerange) # timerange秒前までのデータを取得

  # 指定期間の時刻のリストを作成
  time_list = []
  for i in range(1,int(timerange/5)):
    time_list.append(gt + datetime.timedelta(seconds = i*5))
  time_list.append(lt)

  # pcwl情報の取り出し
  pcwlnode = []
  pcwlnode += db.pcwlnode.find({"floor":floor},{"_id":0})

  pfvinfo = [] # 空のpfvinfo生成
  exist_mac = [] #出現中のmacを一時保存
  route_info =[] #経路ごとに格経路パターンを格納
  for i in range(0,len(pcwlnode)):
    for j in range(0,len(pcwlnode)):
      st = pcwlnode[i]["pcwl_id"] # 出発点
      ed = pcwlnode[j]["pcwl_id"] # 到着点
      # iとjが隣接ならば人流0人でpfvinfoに加える
      if ed in pcwlnode[i]["next_id"]:
        pfvinfo.append({"direction":[st,ed],"size":0})

  for i in range(len(pcwlnode)):
    pcwlnode[i]["mac_len"] = []
    pcwlnode[i]["size"] = 0

  # 時刻ごとに経路情報を作成
  for time in time_list:
    # pfv情報の取り出し
    tmp_pfvinfo = []
    tmp_pfvinfo += db.pfvinfo.find({"datetime":time, "floor":floor}).sort("datetime", ASCENDING)
    pfvmacinfo = []
    pfvmacinfo += db.pfvmacinfo.find({"datetime":time, "floor":floor}).sort("datetime", ASCENDING)
    # 滞留端末情報の取り出し
    stayinfo = []
    stayinfo += db.stayinfo.find({"datetime":time, "floor":floor}).sort("datetime", ASCENDING)
    staymacinfo = []
    staymacinfo += db.staymacinfo.find({"datetime":time, "floor":floor}).sort("datetime", ASCENDING)
    # 全体のデータを作成===========================================================
    if len(tmp_pfvinfo) >= 1:
      for i in range(0,len(tmp_pfvinfo[0]["plist"])):
        pfvinfo[i]["size"] += tmp_pfvinfo[0]["plist"][i]["size"]
    if len(stayinfo) >= 1:
      for i in range(0,len(stayinfo[0]["plist"])):
        pcwlnode[i]["size"] += stayinfo[0]["plist"][i]["size"]
        for new_mac in stayinfo[0]["plist"][i]["mac_list"]:
          if new_mac in pcwlnode[i]["mac_len"]:
            pass
          else :
            pcwlnode[i]["mac_len"] += [new_mac]
    # ===========================================================================

    # 経路情報を作成===============================================================
    # tmp_mac = []
    # for i in pfvmacinfo[0]:
    #   if i["mac"] in exist_mac:
    #     if route_info[i["mac"]]

      # stayinfo = stayinfo[-1]["plist"]
      # for i in range(len(pcwlnode)):
      #   pcwlnode[i]["mac_len"] = len(stayinfo[i]["mac_list"])
      #   pcwlnode[i]["size"] = stayinfo[i]["size"]
      #   pcwlnode[i]["color"] = "red"

  # 最大経路通過数・最多経路順を生成
  max_pfv = 0
  keyfunc_pfv = lambda x:x["size"]
  tmp_sort_pfv = sorted(pfvinfo,key=keyfunc_pfv)
  sort_pfv = []
  for i in tmp_sort_pfv:
    if i["size"] != 0:
      if i["size"] == max_pfv:
        sort_pfv[0]["direction"].append(i["direction"])
      else:
        sort_pfv.insert(0,{"size":i["size"],"direction":[i["direction"]]})
        max_pfv = i["size"]
  if len(sort_pfv) != 0:
    min_pfv = sort_pfv[-1]["size"]
  else:
    min_pfv = 0
  rank_pfv = sort_pfv[:3] #上位3位まで取り出し

  # 滞留回数・端末数の最大･最小および順序を作成
  for i in range(len(pcwlnode)):
    pcwlnode[i]["mac_len"] = len(pcwlnode[i]["mac_len"])
  keyfunc_node = lambda x:x["size"]
  keyfunc_mac = lambda x:x["mac_len"]
  tmp_sort_node = sorted(pcwlnode,key=keyfunc_node)
  tmp_sort_mac = sorted(pcwlnode,key=keyfunc_mac)
  sort_node =[]
  sort_mac = []
  max_node = 0
  max_mac = 0
  for i in tmp_sort_node:
    if i["size"] != 0:
      if max_node == i["size"]:
        sort_node[0]["pcwl_id"].append(i["pcwl_id"])
      else:
        sort_node.insert(0,{"size":i["size"],"pcwl_id":[i["pcwl_id"]]})
        max_node = i["size"]
  if len(sort_node) != 0:
    min_node = sort_node[-1]["size"]
  else:
    min_node = 0
  rank_node = sort_node[:3] #上位3位まで取り出し
  for i in tmp_sort_mac:
    if i["mac_len"] != 0:
      if max_mac == i["mac_len"]:
        sort_mac[0]["pcwl_id"].append(i["pcwl_id"])
      else:
        sort_mac.insert(0,{"mac_len":i["mac_len"],"pcwl_id":[i["pcwl_id"]]})
        max_mac = i["mac_len"]
  if len(sort_mac) != 0:
    min_mac = sort_mac[-1]["mac_len"]
  else:
    min_mac = 0
  rank_mac = sort_mac[:3] #上位3位まで取り出し


  flow_data = {"max":max_pfv,"min":min_pfv,"rank_pfv":rank_pfv}
  ap_data = {"max_node":max_node,"min_node":min_node,"max_mac":max_mac,"min_mac":min_mac}
  # 送信するデータセット
  dataset = {"pfvinfo":pfvinfo,"pcwlnode":pcwlnode,"flow_data":flow_data,"ap_data":ap_data,"rank_pfv":rank_pfv,"rank_node":rank_node,"rank_mac":rank_mac}
  # dataset = {"pfvinfo":pfvinfo}

  return render_json_response(request, dataset) # dataをJSONとして出力