# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from cms.forms import SensorForm
from cms.models import Sensor2, Sensor3, initial_db, temp_db, error_db
from mongoengine import *
from pymongo import *
import requests

import json
import math
import datetime
import locale

from cms.convert_device_id    import convert_device_id
from cms.convert_datetime import datetime_to_12digits, dt_from_str_to_iso, shift_time, dt_from_iso_to_str, dt_insert_partition_to_min, dt_from_iso_to_jap
from cms.convert_sensor_data    import convert_sensor_data

from cms.write_to_mongo import write_to_initial_db, write_to_sensordb

from cms.constmod import ConstClass

device_list     = ConstClass.device_list
ilu_device_list = ConstClass.ilu_device_list

client = MongoClient()
db     = client.sensordb

device_list     = [1, 2, 3, 4, 5]
ilu_device_list = [4, 8, 9, 18, 20]

# 今日の日付
d = datetime.datetime.today() # 2014-11-20 19:41:51.011593
d = str(d.year)+("0"+str(d.month))[-2:]+("0"+str(d.day))[-2:]+("0"+str(d.hour))[-2:]+("0"+str(int(d.minute/5)*5))[-2:] # 201411201940

##- 外部ファイルをD3で読み込んで表示させる方法 -##
# 1.htmlファイルと読み込むファイル(.csv, .tsv, .jsonなど)を同じディレクトリに置く。
# 2.コマンドプロンプトを起動し、htmlファイルのあるディレクトリに移動する。
# 3.該当ディレクトリで　python -m http.server 8080 を入力。
# 4.ブラウザで http://localhost:8080/ にアクセス

# データリスト画面 http://localhost:8000/cms/data_list/
def data_list(request, limit=100, date_time=d):
 
  # 日付をstr12桁に合わせる --> 2014-11-20 19:40
  date_time = datetime_to_12digits(date_time)

  # データベースから取り出し
  t = Sensor2.objects(datetime__gte="2015-06-29 12:40",device_id=66).order_by("-datetime").limit(5500)

  return render_to_response('cms/data_list.html',  # 使用するテンプレート
                              {'t': t, 'limit':limit, 'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]} )

# データリスト画面 http://localhost:8000/cms/data_list2/
def data_list2(request, limit=100, date_time=d):

  date_time = datetime_to_12digits(date_time)

  lmt = '50' # 親機1台につき取得するデータの件数
  datetime = '"201411101700"' # データ取得時刻
  s = []
  for num in "6789": # 親機ループ 6~9

    r = requests.get('http://api1.ginga-box.com:8080/ginga/sol?mode=getdata&v={box_id:"9CBD9D01000'+num+'", limit:'+lmt+', datetime:'+datetime+'}')
    t = r.json()

    # データの加工
    for i in range(len(t)):
      t[i] = convert_sensor_data(t[i])
    s+=t
    # s = sorted(s.keys("datetime"))
  
  return render_to_response('cms/data_list.html',  # 使用するテンプレート
                              {'t': s, 'limit':limit, 'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]} )

# データ件数確認用・エラーログ用
def data_check(request, date_time=d):

  # 文字列を12桁に合わせる
  date_time = datetime_to_12digits(date_time)

  # データベースから取り出し
  # t = Sensor2.objects(datetime__lt=date_time).order_by("-datetime").limit(int(limit))

  error_data = Sensor2.objects(datetime__lt=date_time, error_flag=True).order_by("-datetime")

  total = Sensor2.objects(datetime__lt=date_time, error_flag=False).count()
  total_e = Sensor2.objects(datetime__lt=date_time, error_flag=True).count()
  total_ini = initial_db.objects(datetime__lt=date_time).count()
  data = []
  t = []

  for s in device_list:
    d0 = s
    d1 = Sensor2.objects(device_id=s, datetime__lt=date_time, error_flag=False).count()
    d2 = Sensor2.objects(device_id=s, datetime__lt=date_time, error_flag=True).count()
    d3 = initial_db.objects(device_id=s, datetime__lt=date_time).count()
    d4 = Sensor2.objects(device_id=s, datetime__lt=date_time, error_flag=False).order_by("-datetime").limit(1).scalar("datetime")

    for i in d4:
      d4 = i
    tmp_list = (d0, d1, d2, d3, d4),
    t += tmp_list

  for i in range(0,len(t)):
    data.append({
      'device_id':t[i][0],
      'data':t[i][1],
      'error':t[i][2],
      'initial':t[i][3],
      'datetime':t[i][4]      
      })

  return render_to_response('cms/data_check.html',  # 使用するテンプレート
                              {'data': data, 'total': total, 'total_e': total_e, 'total_ini': total_ini, 
                              'error_data': error_data,'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]})

  #  検索条件詳細：http://kitanokumo.hatenablog.com/entry/2014/02/04/042222
  
#データ統合用　http://localhost:8000/cms/save_db/
def save_db(request):
  # DB初期化
  Sensor2.objects.all().delete()
  # error_db.objects.all().delete()

  limit = '120000' # 親機1台につき取得するデータの件数
  datetime = '"201411101700-201505280000000"' # データ取得時刻
  for num in "67": # 親機ループ

    url = 'http://api1.ginga-box.com:8080/ginga/sol?mode=getdata&v={box_id:"9CBD9D01000'+num+'",limit:'+limit+',datetime:'+datetime+'}'
    r = requests.get(url)
    t = r.json()
    
    # データの加工
    for i in range(len(t)):
      t[i] = convert_sensor_data(t[i])

      # データ登録
      if(t[i]["sensor_id"] == "初期データ"):
        pass

      else:
        write_to_sensordb(t[i])

  t = Sensor2.objects().all().order_by("-date", "-time").limit(100)

  return render_to_response('cms/save_db.html',  # 使用するテンプレート
                              {'t': t} )

# センサーマップ画面 http://localhost:8000/cms/sensor_map/
def sensor_map(request, date_time=d, type="20"):

  import datetime

  # 文字列を12桁に合わせる
  date_time = datetime_to_12digits(date_time)

  onehour_ago = datetime.datetime(int(date_time[0:4]),int(date_time[5:7]),int(date_time[8:10]),int(date_time[11:13]),int(date_time[14:16]))
  onehour_ago -= datetime.timedelta(hours = 1)
  onehour_ago = str(onehour_ago.year)+"-"+("0"+str(onehour_ago.month))[-2:]+"-"+("0"+str(onehour_ago.day))[-2:]+" "+("0"+str(onehour_ago.hour))[-2:]+":"+("0"+str(onehour_ago.minute))[-2:]

  # db.Sensor2.create_index([("device_id",ASCENDING),("datetime",DESCENDING)])

  # データベースから取り出し
  t = []
  t_ilu = []
  # for s in device_list:
  #   start = datetime.datetime.today()
  #   if db.sensor2.find({"device_id":s, "datetime":{"$gte":onehour_ago, "$lte":date_time}, "error_flag":False}).count() != 0:
  #     t += db.sensor2.find({"device_id":s, "datetime":{"$gte":onehour_ago, "$lte":date_time}, "error_flag":False}).sort("datetime")[1]
  #   # t += Sensor2.objects(device_id=s, datetime__gt=onehour_ago, datetime__lt=date_time, error_flag=False).order_by("-datetime").limit(1)
  #   end = datetime.datetime.today()
  #   print (end - start)

  # for s in ilu_device_list:
  #   start = datetime.datetime.today()
  #   if db.sensor2.find({"device_id":s, "datetime":{"$gte":onehour_ago, "$lte":date_time}, "error_flag":False}).count() != 0:
  #     t_ilu += db.sensor2.find({"device_id":s, "datetime":{"$gte":onehour_ago, "$lte":date_time}, "error_flag":False}).sort("-datetime")[1]
  #   # t += Sensor2.objects(device_id=s, datetime__gt=onehour_ago, datetime__lt=date_time, error_flag=False).order_by("-datetime").limit(1)
  #   end = datetime.datetime.today()
  #   print (end - start)

  # 最近の取得時間の取り出し
  db.Sensor2.create_index([("datetime",DESCENDING)])

  recent = []
  num = 10 # 最大取り出し件数
  today = datetime.datetime.today()

  lt = today - datetime.timedelta(hours = today.hour) - datetime.timedelta(minutes = today.minute + 5)
  gt = today - datetime.timedelta(days = 20)
  # print (lt, gt)

  # tmp_date = dt_from_iso_to_str(today)[:8]
  # dt_datas = list(db.sensor2.find({"datetime":{"$gte":gt, "$lte":lt}, "error_flag":False},{"datetime":1}).sort("datetime", DESCENDING))
  
  # if len(dt_datas) > 0:
  #   for i in range(0, len(dt_datas) - 1):
  #     dt_data = dt_datas[i]

  #     if str(dt_from_iso_to_str(dt_data["datetime"]))[:8] != tmp_date[:8]:
  #       tmp = [dt_data["datetime"]]
  #       recent += tmp

  #     tmp_date = str(dt_from_iso_to_str(dt_data["datetime"]))[:8]
  #     print (tmp_date)

  # else:
  #   recent += [today]

  #   print ("aaaaaaaaaaaaaaa", recent)
  #   pass



  for i in range(0,num - 1):
    # start = datetime.datetime.today()
    if len(recent) > i :
      # lt = recent[i] - datetime.timedelta(hours = recent[i].hour) - datetime.timedelta(minutes = recent[i].minute + 5)
      # gt = recent[i] - datetime.timedelta(days = 30)
      # start = datetime.datetime.today()
      if db.sensor2.find({"datetime":{"$lte":lt, "$gte":gt}, "error_flag":False}).count() != 0:
        # end = datetime.datetime.today()
        # print ("if:", end - start)

        # start = datetime.datetime.today()
        tmp = db.sensor2.find({"datetime":{"$lte":lt, "$gte":gt}, "error_flag":False},{"datetime":1}).sort("-datetime")[1]
        # end = datetime.datetime.today()
        # print ("tmp:", end - start)

        tmp = [tmp["datetime"]]
        # print (type(tmp))
        recent += tmp
      recent += Sensor2.objects(datetime__lt=lt, error_flag=False).order_by("-datetime").limit(1).scalar("datetime")
    # end = datetime.datetime.today()
    # print ("running:",end - start)

  return render_to_response('cms/sensor_map.html',  # 使用するテンプレート
                              {'t': t, 't_ilu': t_ilu,'recent': recent, 'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]
                              ,'sensor':type[0:1],'visualize':type[1:2]} )

# センサーグラフ画面 http://localhost:8000/cms/sensor_graph/
def sensor_graph(request, limit=100, date_time=d, type="101"):

  # 文字列を12桁に合わせる
  date_time = datetime_to_12digits(date_time)

  # 直近2日分を取得
  two_days_ago = dt_from_str_to_iso(date_time)
  two_days_ago -= datetime.timedelta(days = 2)
  two_days_ago = dt_from_iso_to_str(two_days_ago)
  two_days_ago = dt_insert_partition_to_min(two_days_ago)

  # データベースから取り出し
  t = Sensor2.objects(device_id=type[1:4],datetime__gt=two_days_ago, datetime__lte=date_time, error_flag=False).order_by("-datetime").limit(int(limit))

  return render_to_response('cms/sensor_graph.html',  # 使用するテンプレート
                              {'t': t, 'limit':limit, 'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]
                              ,'sensor': type[0:1],'device_id':type[1:4]} )

def save_db_heat(request): #登録時は下記コメントアウトを解除
  """
  temp_db.objects.all().delete()
  data_all = Sensor2.objects(device_id__ne="Error")

  s_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 36, 37, 46]
  var_dt = datetime.datetime(2014, 11, 10, 17, 00, 00)
  while var_dt < datetime.datetime(2014, 11, 13, 19, 00, 00):
    data_ext = data_all.filter(datetime__gte = var_dt).filter(datetime__lt = var_dt + datetime.timedelta(hours=1))

    for sid in s_list: 
      tmp_tu = 0 
      t = data_ext.filter(device_id = sid)

      if(len(t) != 0):
        lc = 0    #ループカウンタ

        for i in range(len(t)):
          tmp_tu += t[i]["tu"]
          lc += 1
      
        tmp_tu = tmp_tu / lc

        save2mongo = temp_db(
                         device_id = t[i]["device_id"],
                         #pos_x = tmp_pos_x,
                         #pos_y = tmp_pos_y,
                         tu = round(tmp_tu, 1),
                         date = str(var_dt)[0:10],
                         time = str(var_dt)[11:13]               
                         )
        save2mongo.save()

    var_dt += datetime.timedelta(hours=1)

  """
  t = temp_db.objects().order_by("-date", "-time").limit(10)

  return render_to_response('cms/save_db_heat.html',  # 使用するテンプレート
                    {'t': t } )

#データ更新・追加用　http://localhost:8000/cms/~
def update_db(request):

  # Sensor3.objects.all().delete()
  # error_db.objects.all().delete()

  limit = '1000' # 親機1台につき取得するデータの件数
  datetime = '"201506010000"' # 取得時間帯
  for num in "6789": # 親機ループ

    r = requests.get('http://api1.ginga-box.com:8080/ginga/sol?mode=getdata&v={box_id:"9CBD9D01000'+num+'", limit:'+limit+'}')
    t = r.json()

    # 最新データ取り出し
    latest_data = Sensor2.objects(box_id="9CBD9D01000"+num+"").order_by("-datetime").limit(1)

    if(latest_data.count() == 0):
      latest_datetime = str("2014-11-10 00:00:00.000")
      latest_datetime = dt_from_str_to_iso(latest_datetime)
    else:
      latest_datetime = latest_data[0]["datetime"]

    # データの加工
    for i in range(len(t)):
      t[i] = convert_sensor_data(t[i])

      dt = dt_from_str_to_iso(t[i]["datetime"])

      latest_datetime = shift_time(dt)

      # データ登録
      if(dt <= latest_datetime):
        break

      else:
        # 初期データ
        if(t[i]["sensor_id"] == "初期データ"):
          pass
        # エラーデータ
        elif(t[i]["sensor_id"] == "Error"):
          pass
        # 計測データ
        else:
          write_to_sensordb(t[i])

  t = Sensor2.objects().all().order_by("-datetime").limit(30)

  return render_to_response('cms/update_db.html',  # 使用するテンプレート
                              {'t': t} )

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

# JSONを返すビュー http://localhost:8000/cms/response_json/
def response_json(request, date_time=d):

  import datetime

  if (date_time == d):
    _15min_ago = datetime.datetime.today() - datetime.timedelta(minutes = 15)
    _15min_ago = dt_from_iso_to_str(_15min_ago)

    # Sensor2.objects.all().delete()
    limit = '60' # 親機1台につき取得するデータの件数
    datetime = _15min_ago + "-" + d

    date_time = dt_insert_partition_to_min(date_time)
    _15min_ago = dt_insert_partition_to_min(_15min_ago)
    _15min_ago = dt_from_str_to_iso(_15min_ago)

    # データベースから取り出し
    aggregated_data = db.sensor2.aggregate([{ "$match" :{"datetime":{"$gte":_15min_ago, "$lte":date_time}, "error_flag":False} },
     { "$group" : {"device_id":"$device_id", "count" : {"$sum" : 1 } } }])
   
    device_list     = aggregated_data["result"]
    ilu_device_list = [4, 8, 9, 18, 20]
    print (device_list)

    t = []
    up2date = Sensor2.objects(error_flag=False).order_by("-datetime").limit(1).scalar("datetime") # 最新時刻
    for s in device_list:
      t += Sensor2.objects(device_id=s, datetime__gt=_15min_ago, error_flag=False).order_by("-datetime").limit(1).scalar("ac","ilu","tu","pos_x","pos_y","device_id","box_id","datetime")
      
    # Python辞書オブジェクトとしてdataに格納
    data = []
    for i in range(0,len(t)):
      data.append({
        'ac':t[i][0],
        'ilu':t[i][1],
        'tu':t[i][2],
        'pos_x':t[i][3],
        'pos_y':t[i][4],
        'device_id':t[i][5],
        'box_id':t[i][6],
        'datetime':dt_from_iso_to_jap(t[i][7]),
        'up2date':dt_from_iso_to_jap(up2date[0]),
        })
    
    # r = requests.get('http://api1.ginga-box.com:8080/ginga/sol?mode=getdata&v={box_id:"9CBD9D010006", limit:50, datetime:"201411101700-201411101900"}')

  else:
    date_time = dt_insert_partition_to_min(date_time)
    onehour_ago = dt_from_str_to_iso(date_time) - datetime.timedelta(hours = 1)
    # onehour_ago = str(onehour_ago.year)+"-"+("0"+str(onehour_ago.month))[-2:]+"-"+("0"+str(onehour_ago.day))[-2:]+" "+("0"+str(onehour_ago.hour))[-2:]+":"+("0"+str(onehour_ago.minute))[-2:]

    # データベースから取り出し

    aggregated_data = db.sensor2.aggregate([{ "$match" :{"datetime":{"$gte":onehour_ago, "$lte":date_time}, "error_flag":False} },
     { "$group" : {"device_id":"$device_id", "count" : {"$sum" : 1 } } }])
   
    device_list     = aggregated_data["result"]
    ilu_device_list = [4, 8, 9, 18, 20]
    print (device_list)

    t = []
    for s in device_list:
      t += Sensor2.objects(device_id=s, datetime__gt=onehour_ago, datetime__lt=date_time, error_flag=False).order_by("-datetime").limit(1).scalar("ac","ilu","tu","pos_x","pos_y","device_id","box_id","datetime")
      
    # Python辞書オブジェクトとしてdataに格納
    data = []
    for i in range(0,len(t)):
      data.append({
        'ac':t[i][0],
        'ilu':t[i][1],
        'tu':t[i][2],
        'pos_x':t[i][3],
        'pos_y':t[i][4],
        'device_id':t[i][5],
        'box_id':t[i][6],
        'datetime':dt_from_iso_to_jap(t[i][7])
        })

  return render_json_response(request, data) # dataをJSONとして出力

# d3.jsテスト画面 http://localhost:8000/cms/d3jstest/
def d3jstest(request):

  t = []
  for s in device_list:
    t += list(Sensor2.objects(device_id=s).order_by("-datetime").limit(1))

  return render_to_response('cms/d3jstest.html',  # 使用するテンプレート
                              {'t':t} )      # テンプレートに渡すデータ 
  
# センサーマップ画面(英語版) http://localhost:8000/cms/sensor_map_en/
def sensor_map_en(request, date_time=d, type="20"):

  import datetime

  # 文字列を12桁に合わせる
  date_time = datetime_to_12digits(date_time)

  onehour_ago = datetime.datetime(int(date_time[0:4]),int(date_time[5:7]),int(date_time[8:10]),int(date_time[11:13]),int(date_time[14:16]))
  onehour_ago -= datetime.timedelta(hours = 1)
  onehour_ago = str(onehour_ago.year)+"-"+("0"+str(onehour_ago.month))[-2:]+"-"+("0"+str(onehour_ago.day))[-2:]+" "+("0"+str(onehour_ago.hour))[-2:]+":"+("0"+str(onehour_ago.minute))[-2:]

  # データベースから取り出し
  t = []
  t_ilu = []

  for s in device_list:
    t += Sensor2.objects(device_id=s, datetime__gt=onehour_ago, datetime__lt=date_time, error_flag=False).order_by("-datetime").limit(1)

  for s in ilu_device_list:
    t_ilu += Sensor2.objects(device_id=s, datetime__gt=onehour_ago, datetime__lt=date_time, error_flag=False).order_by("-datetime").limit(1)

  # 最近の取得時間の取り出し
  recent = []
  num = 5 # 最大取り出し件数
  today = datetime.datetime.today()
  recent += Sensor2.objects(datetime__lt=today, error_flag=False).order_by("-datetime").limit(1).scalar("datetime")

  for i in range(0,num - 1):
    if len(recent) > i :
      lt = recent[i] - datetime.timedelta(hours = recent[i].hour) - datetime.timedelta(minutes = recent[i].minute + 5)
      recent += Sensor2.objects(datetime__lt=lt, error_flag=False).order_by("-datetime").limit(1).scalar("datetime")

  return render_to_response('cms/sensor_map_en.html',  # 使用するテンプレート
                              {'t': t, 't_ilu': t_ilu,'recent': recent, 'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]
                              ,'sensor':type[0:1],'visualize':type[1:2]} )

# センサーグラフ画面(英語版) http://localhost:8000/cms/sensor_graph_en/
def sensor_graph_en(request, limit=100, date_time=d, type="101"):

  # 文字列を12桁に合わせる
  date_time = datetime_to_12digits(date_time)

  # 直近2日分を取得
  two_days_ago = dt_from_str_to_iso(date_time)
  two_days_ago -= datetime.timedelta(days = 2)
  two_days_ago = dt_from_iso_to_str(two_days_ago)
  two_days_ago = dt_insert_partition_to_min(two_days_ago)

  # データベースから取り出し
  t = Sensor2.objects(device_id=type[1:4],datetime__gt=two_days_ago, datetime__lte=date_time, error_flag=False).order_by("-datetime").limit(int(limit))

  return render_to_response('cms/sensor_graph_en.html',  # 使用するテンプレート
                              {'t': t, 'limit':limit, 'year':date_time[0:4],'month':date_time[5:7]
                              ,'day':date_time[8:10],'hour':date_time[11:13],'minute':date_time[14:16]
                              ,'sensor': type[0:1],'device_id':type[1:3]} )
