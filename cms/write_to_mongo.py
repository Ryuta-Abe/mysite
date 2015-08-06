import datetime
from cms.forms import SensorForm
from cms.models import Sensor2, Sensor3, initial_db, temp_db, error_db
from mongoengine import *
from pymongo import *

from cms.convert_datetime import dt_from_str_to_iso

from cms.constmod import ConstClass

device_list = ConstClass.device_list
ilu_device_list = ConstClass.ilu_device_list

def write_to_initial_db(s):
	save2mongo = initial_db(
                         box_id = s["box_id"],
                         device_id = s["device_id"],
                         date = s["date"],
                         time = s["time"],
                         datetime = s["datetime"]                 
                         )
	save2mongo.save()

def write_to_errordb(s):
	pass

def write_to_sensordb(s):

	s["datetime"] = dt_from_str_to_iso(s["datetime"])
	time_interval = s["datetime"] + datetime.timedelta(seconds = 2)

	# 直近2秒以内に同じdevice_idのものがあれば統合
	if(Sensor2.objects(datetime__gte=s["datetime"]).filter(datetime__lte=time_interval).filter(device_id=s["device_id"]).count()==1):
		save2mongo = Sensor2.objects(datetime__gte=s["datetime"]).filter(datetime__lte=time_interval).filter(device_id=s["device_id"]).get()

	else:
		save2mongo = Sensor2(
	                       box_id = s["box_id"],
	                       device_id = s["device_id"],
	                       pos_x = s["pos_x"],
	                       pos_y = s["pos_y"],
	                       # rssi  = s["rssi"], 
	                       date  = s["date"],
	                       time  = s["time"],
	                       datetime = s["datetime"]                           
	                       )

	# RSSIがあれば登録
	if (("rssi" in s) == True):
		save2mongo.rssi = float(s["rssi"])

	# エラーフラグ追加
	if(s["sensor_id"] == "Error"):
		save2mongo.error_flag  = True
	else:
		save2mongo.error_flag  = False

	# 各センサー計測値追加
	if(s["sensor_id"] == "加速度"):
		save2mongo.ac  = s["ac"]
	elif(s["sensor_id"] == "照度"):
		save2mongo.ilu = s["ilu"]
	elif(s["sensor_id"] == "赤外線"):
		save2mongo.tu = s["tu"]

	# 照度あり・なし分類
	if(s["device_id"] in ilu_device_list):
		save2mongo.sensor_type = "照度あり"
	else:
		save2mongo.sensor_type = "照度なし"
		save2mongo.ilu = 0

	# データ登録
	save2mongo.save()
