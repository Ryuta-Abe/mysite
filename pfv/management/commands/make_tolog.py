# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from pymongo import *
from mongoengine import *
from pfv.models import timeoutlog, pcwliplist, tmptolog, hourlytolog
from pfv.convert_datetime import *

# mongoDBに接続
client = MongoClient()
db = client.nm4bd

class Command(BaseCommand):
  help = u'aggregate timeout-logs'

  def handle(self, *args, **options):

	  cond = {"$limit":1000000}
	  col_name = timeoutlog
	  ag = col_name._get_collection().aggregate([
		                                            cond,
		                                            {"$group":
		                                              {"_id":
		                                                {"timeout_ip":"$timeout_ip",
		                                                },
		                                               "count":{"$sum":1},
		                                              },
		                                            },
		                                            {"$out": "tmptolog"},
		                                          ],
		                                        allowDiskUse=True,
		                                        )

	  print("aggregate finish")

	  datas = db.tmptolog.find()
	  for data in datas:
	  	ip = data["_id"]["timeout_ip"]
	  	ip_list = db.pcwliplist.find_one({"ip":ip})
	  	data["floor"] = ip_list["floor"]
	  	data["pcwl_id"] = ip_list["pcwl_id"]
	  	data["ip"] = data["_id"]["timeout_ip"]
	  	del(data["_id"])
	  	db.tmptolog.save(data)

	  
