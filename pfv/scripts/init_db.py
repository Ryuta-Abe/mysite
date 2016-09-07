# -*- coding: utf-8 -*-

# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

db.rttmp.drop()
db.trtmp.drop()
db.pfvinfo.drop()
db.pfvmacinfo.drop()
db.stayinfo.drop()
db.staymacinfo.drop()
db.pcwltime.drop()
db.pastdata.drop()
