# -*- coding: utf-8 -*-
from pymongo import *
from convert_ip import *
from convert_datetime import *

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
#   mongo nm4bd --quiet --eval "for (key in db.hourlytolog.findOne()) print(key)" > dbm_field.txt
# 4.フィールド一覧ソート
#   py txt_sort.py fields.txt
# 5.不要なフィールド(_id等)削除 & datetime先頭に移動

# 6.mongoexport実行
#   mongoexport --sort {"datetime":1} -d nm4bd -c dbmlog -o dbm19_1c.csv --csv --fieldFile dbm_field.txt

db.dbmlog.drop()
# db.test2.drop()
# datas = db.test.find({"mac":{"$regex":"00:11:81:10:01:"}})
# for data in datas:
#     tmp_dict = convert_ip(data["ip"])
#     data["floor"], data["pcwl_id"] = tmp_dict["floor"], tmp_dict["pcwl_id"]
#     print(data)
#     db.test2.insert(data)

iso_st = dt_from_14digits_to_iso("20161128160100")
# iso_st = dt_from_14digits_to_iso("20161124175500")
# iso_ed = dt_from_14digits_to_iso("20161124175530")
iso_ed = dt_from_14digits_to_iso("20161128162100")

mac = "00:11:81:10:01:17"
floor = "W2-9F"

ip_list = []
ip_list += db.pcwliplist.find({"floor":floor})
for ip_data in ip_list:
    # ip_data = {"floor":ip_data["floor"], "pcwl_id":ip_data["pcwl_id"]}
    ip_data["log_key"] = str(ip_data["floor"]) + "-" + str(ip_data["pcwl_id"])

print("from:" + str(iso_st))
print("to  :" + str(iso_ed) + "\n")
gte = iso_st
lt  = shift_seconds(gte, 5)

while (lt <= iso_ed):
    print(gte)
    data_5s = {}
    data_5s["datetime"] = gte
    for ip_data in ip_list:
        ip = str(ip_data["ip"])
        # print(ip)
        dbm_data = db.test2.find_one({"mac":mac, "get_time_no":{"$gte":gte,"$lt":lt},"ip":ip})
        # print(dbm_data)
        if (dbm_data != None):
            data_5s[ip_data["log_key"]] = dbm_data["dbm"]
        else:
            data_5s[ip_data["log_key"]] = None
            
    db.dbmlog.insert(data_5s)
    
    gte = shift_seconds(gte,5)
    lt  = shift_seconds(gte,5)

# 00:11:81:10:01:1c
# 00:11:81:10:01:19
# 00:11:81:10:01:17
# 00:11:81:10:01:1a



