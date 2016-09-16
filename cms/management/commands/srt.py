# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from cms.models import Sensor2

import json
import math
import datetime
import locale
from datetime import datetime, timedelta
import time
import requests

from cms.convert_device_id import *
from cms.convert_datetime import *
from cms.convert_sensor_data import *
from cms.write_to_mongo import *

# mongoDBに接続
client = MongoClient()
db = client.sensordb

limit = '100' # 親機1台につき取得するデータの件数
datetime = '"201412091900"' # 取得時間帯
# box_list = ["06","07","08","09","0A","0B","0C","0D","0E","0F"]
box_list = ["0B","0A"]

class Command(BaseCommand):
  # args = '<target_id target_id ...>'
  help = u'RealTime process'

  def handle(self, *args, **options):
    for num in box_list: # 親機ループ

      r = requests.get('http://api1.ginga-box.com:8080/ginga/sol?mode=getdata&v={box_id:"9CBD9D0100'+num+'", limit:'+limit+'}', timeout=120)
      t = r.json()

      # 最新データ取り出し
      latest_data = Sensor2.objects(box_id="9CBD9D0100"+num+"").order_by("-datetime").limit(1)

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


