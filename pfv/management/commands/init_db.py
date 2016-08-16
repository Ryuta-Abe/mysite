# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd


class Command(BaseCommand):
  # args = '<target_id target_id ...>'
  help = u'Initialize DBs'

  def handle(self, *args, **options):
	db.pfvinfo.drop()
	db.pfvmacinfo.drop()
	db.stayinfo.drop()
	db.staymacinfo.drop()
	db.pcwltime.drop()
	db.pastdata.drop()
