# -*- coding: utf-8 -*-
# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

REMOVE_RAWDATA = False

def init_db():
	if REMOVE_RAWDATA:
		db.rttmp.drop()
		db.trtmp.drop()
	db.pfvinfo.drop()
	db.pfvmacinfo.drop()
	db.stayinfo.drop()
	db.staymacinfo.drop()
	db.pcwltime.drop()
	db.pastdata.drop()
	db.tmpcol_backup.drop()
	db.examine_route.drop()
	db.examine_summary.drop()
	db.analy_coord.drop()
	print("successfully dropped all DBs!")

if __name__ == '__main__':
    init_db()
    