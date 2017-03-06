# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
# mongoDBに接続
from pymongo import *
import time
client = MongoClient()
db = client.nm4bd

class Command(BaseCommand):
  # args = '<target_id target_id ...>'
  help = u'django command test'

  def handle(self, *args, **options):

    def convert_ip(ip): #function which can get floor and pcwl_id info. from ip-address
      ip_dict = db.pcwliplist.find_one({"ip":ip},{"_id":False,"floor":True,"pcwl_id":True}) #pick up what is needed 
      if ip_dict is None: #exception handling
        ip_dict = {"floor":"Unknown","pcwl_id":9999}
      return ip_dict
    
    st = time.time()
    for i in range(100):
      ip_list = []
      ip_list = [convert_ip("10.0.11.33"),convert_ip("10.0.11.35"),convert_ip("10.0.11.15"),convert_ip("10.0.11.13"),convert_ip("10.0.11.11"),
                 convert_ip("10.0.11.7"),convert_ip("10.0.12.77"),convert_ip("10.0.12.75"),convert_ip("10.0.11.147"),convert_ip("10.0.11.149")]
    print(ip_list)
    ed = time.time()
    print(ed - st)
    st = time.time()
    for i in range(100):
      id_list = []
      id_list = [convert_nodeid(1246),convert_nodeid(1248),convert_nodeid(1250),convert_nodeid(1252),convert_nodeid(1254),
                 convert_nodeid(1256),convert_nodeid(1258),convert_nodeid(1260),convert_nodeid(1263),convert_nodeid(1265)]
    print(id_list)
    ed = time.time()
    print(ed - st)
