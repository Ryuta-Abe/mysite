# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
from time import sleep
import random

# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

def on_connect(client, userdata, rc):
  print("Connected with result code " + str(rc))

def on_disconnect(client, userdata, rc):
  if rc != 0:
     print("Unexpected disconnection.")

def on_publish(client, userdata, mid):
  print("publish: {0}".format(mid))

def main(light_list):
  client = mqtt.Client()
  client.on_connect = on_connect
  client.on_disconnect = on_disconnect
  client.on_publish = on_publish
  client.username_pw_set("spark","hogehoge")
  client.connect("localhost", 1883, 60)

  client.loop_start()
  msg = ""
  num = 0
  for light in light_list:
    if (light):
      msg_num = num
      msg = msg + str(msg_num)
      # sleep(0.25)
    num += 1
  print(msg)
  client.publish("test_sub", msg, qos=1)
  # client.publish("test_sub", "012")
  client.disconnect()

if __name__ == '__main__':

  param = sys.argv
  st_dt = dt_end_to_05(str(param[1]))
  st_dt = dt_from_14digits_to_iso(st_dt)
  st_dt = shift_seconds(st_dt, -5)
  main(st_dt)