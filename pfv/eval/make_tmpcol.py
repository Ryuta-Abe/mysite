# -*- coding: utf-8 -*-
# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from convert_ip import *
from convert_datetime import *
import csv

from pymongo import *
client = MongoClient()
db = client.nm4bd

# 0. python C:\Users\Ryuta\Desktop\my_script\csv_reform.py
# 1. mongoimport -d nm4bd -c csvtest --headerline --type csv C:\Users\Ryuta\Desktop\analyze_data\exp_param_conv.csv --drop
# 2-1. python C:\Users\Ryuta\Desktop\my_script\extract_tag.py rttmp_yyyymmdd.json
# 2-2. mongoimport -d nm4bd -c test2 rttmp_yyyymmdd.json

### ("fields.txt"が存在しない場合は3-5を行う) ###
### 3.key一覧取得
###   mongo nm4bd --quiet --eval "for (key in db.hourlytolog.findOne()) print(key)" > dbm_field.txt
### 4.フィールド一覧ソート
###   py txt_sort.py fields.txt
### 5.不要なフィールド(_id等)削除 & datetime先頭に移動
###########################################

# 6. python C:\Users\Ryuta\workspace_env3\mysite\pfv\scripts\make_tmpcol.py
# 7.mongoexport実行
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
                
        db.dbmlog.insert(data_5s)

        # if exist_flag:
        #     db.dbmlog.insert(data_5s)
        # else:
        #     print("None data : "+str(gte))
        
        gte = shift_seconds(gte,5)
        lt  = shift_seconds(gte,5)


def replace_and_make_label(input_file, label_file, node_id):
    '''
    テキストファイルの全ての行に共通の置換処理を行う．
    '''
    output_file = input_file + "_replace.csv"
    # 出力ファイルの初期化（削除）
    if os.path.exists(output_file):
        os.remove(output_file)

    # f_output_file = open(output_file, "a")
    # f_input_file = open(input_file, 'r')
    f_label = open(label_file, "a",newline='')
    label_writer = csv.writer(f_label)
    with open(input_file, "r") as f_in:
        csv_reader = csv.reader(f_in, delimiter=",", quotechar='"')
        f = open(output_file, 'w',newline='')
        writer = csv.writer(f)

        # 1行ずつ処理．
        cnt = 0
        datas = []
        ldatas = []
        for row in csv_reader:
            if cnt != 0:
                datas.append(row)
                ldatas.append([node_id])
            cnt += 1
        writer.writerows(datas)
        label_writer.writerows(ldatas)
        f.close()
    f_in.close()
    f_label.close()
    # csv_reader.close()

    # delete input_file and rename output to input
    os.remove(input_file)
    os.rename(output_file, input_file)


def append_train(input_file, train_file):
    f_train = open(train_file, "a",newline='')
    train_writer = csv.writer(f_train)
    with open(input_file, "r") as f_in:
        csv_reader = csv.reader(f_in, delimiter=",", quotechar='"')

        tr_datas = []
        for row in csv_reader:
            tr_datas.append(row)
        train_writer.writerows(tr_datas)

    f_train.close()



if __name__ == '__main__':
    # common_id_list = ["161207_0", "161208_0"]
    common_id_list = ["170127_"]
    for common_id in common_id_list:
        for id_num in range(1,76):
            id_str = common_id + ("00" + str(id_num))[-3:]
            exp_info = db.csvtest.find_one({"exp_id":id_str})
            print("\n=== " + id_str + " ===")

            ### floor_numは1桁のみ!  ###
            floor = exp_info["floor"]
            # if floor == "W2-8F":
            #     continue
            floor_num = floor[3:4]
            ##########################

            # 実験データ一回分まとめ
            make_dbmlog(exp_info)

            tmp_file_name = 'C:/Users/Ryuta/csv/tmp_' + id_str +'.csv'
            out_file_name = 'C:/Users/Ryuta/csv/' + id_str +'.csv'
            label_file = 'C:/Users/Ryuta/csv/' + common_id + floor +'_label.csv'
            train_file = 'C:/Users/Ryuta/csv/' + common_id + floor +'_train.csv'
            command = 'mongoexport --sort {"datetime":1} -d nm4bd -c dbmlog -o '+ tmp_file_name +' --csv --fieldFile C:/Users/Ryuta/dbm_field'+ floor_num +'.txt'

            # RSSIデータCSV出力
            os.system(command)

            # 1行目削除
            with open(tmp_file_name, 'r') as f:
                doc = [row for row in csv.reader(f, delimiter='\t')]

            # print(doc)
            # for row in doc:
            #     row.pop(0)  #削除したい列が2列目(bの列)なので、1を指定
            del doc[0]

            with open(out_file_name, 'w') as f:
                w = csv.writer(f, delimiter='\t', lineterminator='\n')  #列区切りと行区切りの文字を指定
                w.writerows(doc)

            os.remove(tmp_file_name)
            # 1行目削除 & ラベルデータ作成
            # replace_and_make_label(file_name, label_file, exp_info["st_node"])
            
            # trainデータ作成
            # append_train(file_name, train_file)