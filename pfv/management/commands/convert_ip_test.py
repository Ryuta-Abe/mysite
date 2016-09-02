# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from pfv.convert_nodeid import *
# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

class Command(BaseCommand):
  # args = '<target_id target_id ...>'
  help = u'django command test'

  def handle(self, *args, **options):
  	def convert_ip(ip):
  		ip_dict = db.pcwliplist.find({"ip":ip},{"id":0,"pcwl_id":1})
  		return ip_dict
  	print("django test")
  	ip_dict = convert_ip("10.0.11.21")
  	print(ip_dict)
  	test_dict = convert_nodeid(1236)
  	print(test_dict)
