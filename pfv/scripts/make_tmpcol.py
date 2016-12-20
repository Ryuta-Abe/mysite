# -*- coding: utf-8 -*-
from pymongo import *
from convert_ip import *
from convert_datetime import *
import os

client = MongoClient()
db = client.nm4bd

# 1. mongoimport -d nm4bd -c csvtest --headerline --type csv exp_param.csv --drop
# 2. mongoimport -d nm4bd -c test2 rttmp_yyyymmdd.json

### ("fields.txt"が存在しない場合は3-5を行う)
### 3.key一覧取得
###   mongo nm4bd --quiet --eval "for (key in db.hourlytolog.findOne()) print(key)" > dbm_field.txt
### 4.フィールド一覧ソート
###   py txt_sort.py fields.txt
### 5.不要なフィールド(_id等)削除 & datetime先頭に移動

# 6. python make tmpcol
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
        exist_flag = False
        for ip_data in ip_list:
            ip = str(ip_data["ip"])
            # print(ip)
            dbm_data = db.test2.find_one({"mac":mac, "get_time_no":{"$gte":gte,"$lt":lt},"ip":ip})
            # print(dbm_data)
            if (dbm_data != None):
                data_5s[ip_data["log_key"]] = dbm_data["dbm"]
                exist_flag = True
            else:
                data_5s[ip_data["log_key"]] = -99
                
        if exist_flag:
            db.dbmlog.insert(data_5s)
        else:
            print("None data : "+str(gte))
        
        gte = shift_seconds(gte,5)
        lt  = shift_seconds(gte,5)

if __name__ == '__main__':
    # common_id_list = ["161207_0", "161208_0"]
    common_id_list = ["161213_0"]
    for common_id in common_id_list:
        # id_list = [73,19]
        # for id_num in id_list:
        for id_num in range(67,68):
            id_str = common_id + ("0" + str(id_num))[-2:]
            exp_info = db.csvtest.find_one({"exp_id":id_str})
            print("\n=== " + id_str + " ===")

            ### floor_numは1桁のみ!  ###
            floor_num = exp_info["floor"][3:4]
            make_dbmlog(exp_info)
            # # print(exp_info)
            command = 'mongoexport --sort {"datetime":1} -d nm4bd -c dbmlog -o C:/Users/Ryuta/csv/' + id_str +'.csv --csv --fieldFile C:/Users/Ryuta/dbm_field'+ floor_num +'.txt'
            # # 9F data
            # command = 'mongoexport --sort {"datetime":1} -d nm4bd -c dbmlog -o C:/Users/Ryuta/csv/' + id_str +'.csv --csv --fieldFile C:/Users/Ryuta/dbm_field9.txt'
            # # 7F data
            # # command = 'mongoexport --sort {"datetime":1} -d nm4bd -c dbmlog -o C:/Users/Ryuta/csv/' + id_str +'.csv --csv --fieldFile C:/Users/Ryuta/dbm_field7.txt'
            os.system(command)
