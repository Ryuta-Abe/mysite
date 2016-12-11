# -*- coding: utf-8 -*-
from pymongo import *
from convert_ip import *
from convert_datetime import *
import os

client = MongoClient()
db = client.nm4bd

##### hourlytolog 作成手順 #####
# 0. /home/murakami2/tolog/tolog_2016mmdd.json にあるtologデータ回収
# 1. mongoimport -d nm4bd -c timeoutlog tolog_2016mmdd.json
# 2. 以下のいづれかを行う
#    py manage.py make_hourlylog mmdd（解析したい日付を4桁で）
#    py manage.py make_hourlylog mmddhhmm mmddhhmm(解析したい日時を8桁で、開始・終了の順に)
#    iso_st,iso_edを設定後、py manage.py make_hourlylog

#  mongoimport -d nm4bd -c csvtest --headerline --type csv [CSV_File.csv] (--drop)

# ("fields.txt"が存在しない場合は3-5を行う)
# 3.key一覧取得
#   mongo nm4bd --quiet --eval "for (key in db.hourlytolog.findOne()) print(key)" > dbm_field.txt
# 4.フィールド一覧ソート
#   py txt_sort.py fields.txt
# 5.不要なフィールド(_id等)削除 & datetime先頭に移動

# 6.mongoexport実行
#   mongoexport --sort {"datetime":1} -d nm4bd -c dbmlog -o dbm19_1c.csv --csv --fieldFile dbm_field.txt


def make_dbmlog(exp_info):
    db.dbmlog.drop()

    floor = exp_info["floor"]
    mac = exp_info["mac"]
    common_dt = str(exp_info["common_dt"])
    st_dt = str(exp_info["st_dt"])
    ed_dt = str(exp_info["ed_dt"])
    iso_st = dt_from_14digits_to_iso(common_dt + st_dt)
    iso_ed = dt_from_14digits_to_iso(common_dt + ed_dt)

    print("from:" + str(iso_st))
    print("to  :" + str(iso_ed) + "\n")
    gte = iso_st
    lt  = shift_seconds(gte, 5)

    ip_list = []
    ip_list += db.pcwliplist.find({"floor":floor})
    for ip_data in ip_list:
        ip_data["log_key"] = str(ip_data["floor"]) + "-" + str(ip_data["pcwl_id"])

    # print(lt)
    while (lt <= iso_ed):
        # print(gte)
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

if __name__ == '__main__':
    # common_id_list = ["161207_0", "161208_0"]
    common_id_list = ["161020_0"]
    for common_id in common_id_list:
        # for id_num in range(1,25):
        for id_num in range(17,29):
            id_str = common_id + ("0" + str(id_num))[-2:]
            exp_info = db.csvtest.find_one({"exp_id":id_str})
            make_dbmlog(exp_info)
            # print(exp_info)
            # command = 'mongoexport --sort {"datetime":1} -d nm4bd -c dbmlog -o C:/Users/Ryuta/csv/' + id_str +'.csv --csv --fieldFile C:/Users/Ryuta/dbm_field9.txt'
            command = 'mongoexport --sort {"datetime":1} -d nm4bd -c dbmlog -o C:/Users/Ryuta/csv/' + id_str +'.csv --csv --fieldFile C:/Users/Ryuta/dbm_field7.txt'
            os.system(command)
