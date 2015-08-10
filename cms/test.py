import requests

import convert_device_id
import convert_datetime
import convert_sensor_data

import write_to_mongo

# mongoDBに接続
from mongoengine import *
connect('sensordb')

# クラスの定義
class User(Document):
    name = StringField() #文字列型
    user_number =  IntField() #Int型

#データリスト用
class Sensor2(Document):
    box_id = StringField(max_length=255)
    device_id = IntField()
    # device_id = StringField(max_length=255)
    sensor_type = StringField(max_length=255)
    ac = FloatField()
    pos_x = IntField()
    pos_y = IntField()
    ilu = IntField()
    tu = FloatField()
    datetime = DateTimeField()
    date = StringField(max_length=255)
    time = StringField(max_length=255)
    error_flag = BooleanField()

class Sensor3(Document):
    box_id = StringField(max_length=255)
    device_id = IntField()
    sensor_type = StringField(max_length=255)
    ac = FloatField()
    pos_x = IntField()
    pos_y = IntField()
    ilu = IntField()
    tu = FloatField()
    datetime = DateTimeField()
    date = StringField(max_length=255)
    time = StringField(max_length=255)
    error_flag = BooleanField()

#保存
# user = User()
# user.name = "太朗"
# user.user_number = 3
# user.save()

limit = '50' # 親機1台につき取得するデータの件数
datetime = '"201412091900"' # 取得時間帯
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

# url = 'http://api1.ginga-box.com:8080/ginga/sol?mode=getdata&v={box_id:"9CBD9D010006",limit:20}'
# r = requests.get(url)
# t = r.json()
# print(t)
<<<<<<< .merge_file_QApFma
print("エラー無しやな")
=======
print("エラー無しやな")

# test
# test2
