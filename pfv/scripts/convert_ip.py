# -*- coding: utf-8 -*-
from pymongo import *
client = MongoClient()
db = client.nm4bd

def convert_ip(ip): #function which can get floor and pcwl_id info. from ip-address
  ip_dict = db.pcwliplist.find_one({"ip":ip},{"_id":False,"floor":True,"pcwl_id":True}) #pick up what is needed 
  if ip_dict is None: #exception handling
    ip_dict = {"floor":"Unknown","pcwl_id":9999}
  return ip_dict
