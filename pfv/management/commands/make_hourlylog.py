# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from pymongo import *
from mongoengine import *
# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

# mongoDBに接続
client = MongoClient()
db = client.nm4bd

##### hourlytolog 作成手順 #####
# 0. /home/murakami2/tolog/tolog_2016mmdd.json にあるtologデータ回収
# 1. mongoimport -d nm4bd -c timeoutlog tolog_2016mmdd.json
# 2. 以下のいづれかを行う
#    py manage.py make_hourlylog mmdd（解析したい日付を4桁で）
#    py manage.py make_hourlylog mmddhhmm mmddhhmm(解析したい日時を8桁で、開始・終了の順に)
#    iso_st,iso_edを設定後、py manage.py make_hourlylog

# ("fields.txt"が存在しない場合は3-5を行う)
# 3.key一覧取得
#   mongo nm4bd --quiet --eval "for (key in db.hourlytolog.findOne()) print(key)" > fields.txt
# 4.フィールド一覧ソート
#   py txt_sort.py fields.txt
# 5.不要なフィールド(_id等)削除 & datetime先頭に移動

# 6.mongoexport実行
#   mongoexport --sort {"datetime":1} -d nm4bd -c hourlytolog -o hourlytolog.csv --csv --fieldFile fields.txt


class Command(BaseCommand):
    help = u'aggregate timeout-logs'

    def handle(self, *args, **options):
        interval = 1 ## (h)
        # hourly aggregate
        db.hourlytolog.remove({})
        print(len(args))
        if(len(args) == 1):
            iso_st = dt_from_14digits_to_iso("2016" + args[0] + "000000")
            iso_ed = shift_hours(iso_st,24)
        elif(len(args) == 2):
            iso_st = dt_from_14digits_to_iso("2016" + args[0])
            iso_ed = dt_from_14digits_to_iso("2016" + args[1])
        else:
            iso_st = dt_from_14digits_to_iso("20161012000000")
            iso_ed = dt_from_14digits_to_iso("20161014000000")
            # iso_st = dt_from_14digits_to_iso("20161219160000")
            # iso_ed = dt_from_14digits_to_iso("20161221180000")
        print("from:" + str(iso_st))
        print("to  :" + str(iso_ed) + "\n")
        gte = iso_st
        lt  = shift_hours(gte, interval)
        ip_list = []
        ip_list += db.pcwliplist.find()
        for ip_data in ip_list:
            # ip_data = {"floor":ip_data["floor"], "pcwl_id":ip_data["pcwl_id"]}
            ip_data["log_key"] = str(ip_data["floor"]) + "-" + str(ip_data["pcwl_id"])

        while (lt <= iso_ed):
            print(gte)
            hourly_data = {}
            hourly_data["datetime"] = gte
            for ip_data in ip_list:
                ip = str(ip_data["ip"])
                count_sum = db.timeoutlog.find({"datetime":{"$gte":gte,"$lt":lt},"timeout_ip":ip}).count()
                hourly_data[ip_data["log_key"]] = count_sum

            db.hourlytolog.insert(hourly_data)
            
            gte = shift_hours(gte,interval)
            lt  = shift_hours(gte,interval)
