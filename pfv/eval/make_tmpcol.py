# -*- coding: utf-8 -*-
# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from convert_ip import *
from convert_datetime import *
import csv,glob

from pymongo import *
client = MongoClient()
db = client.nm4bd

# (exp_param.csvにタグのMACアドレスではなく、tag_idを用いている場合)
# 0. python C:\Users\Ryuta\Desktop\my_script\csv_reform.py

# exp_param(教師データ取得stay実験のデータ)のインポート
# 1. mongoimport -d nm4bd -c csvtest --headerline --columnsHaveTypes --type=csv ../../working/exp_param.csv --drop

# jsonファイルからタグのmacアドレスに対応するデータのみを抽出する
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

db.test2.create_index([("mac", ASCENDING),("get_time_no", ASCENDING),("ip",ASCENDING)])

def make_dbmlog(exp_info):
    # """
    # test2コレクション(仮)に入れた、PRデータから
    # 各時刻におけるRSSIパターンデータが入ったコレクション(dbmlog)を作成する
    # @param  exp_info:dict
    # """
    db.dbmlog.drop()

    floor = exp_info["floor"]
    mac = exp_info["mac"]
    common_dt = str(exp_info["common_dt"])
    st_dt = str(exp_info["st_dt"])
    ed_dt = str(exp_info["ed_dt"])
    iso_st = dt_from_14digits_to_iso(common_dt + st_dt)
    iso_ed = dt_from_14digits_to_iso(common_dt + ed_dt)
    print(iso_ed - iso_st)

    print("from:" + str(iso_st))
    print("to  :" + str(iso_ed) + "\n")
    gte = iso_st
    lt  = shift_seconds(gte, 5)

    ip_list = []
    ip_list += db.pcwliplist.find({"floor":floor})
    for ip_data in ip_list:
        ip_data["log_key"] = str(ip_data["floor"]) + "-" + str(ip_data["pcwl_id"])

    while (lt <= iso_ed):
        data_5s = {}
        data_5s["datetime"] = gte
        exist_flag = False
        for ip_data in ip_list:
            ip = str(ip_data["ip"])
            dbm_data = db.test2.find_one({"mac":mac, "get_time_no":{"$gte":gte,"$lt":lt},"ip":ip})
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

# ラベルデータを作成する
def replace_and_make_label(input_file, label_file, node_id):
    '''
    テキストファイルの全ての行に共通の置換処理を行う．
    '''
    output_file = input_file + "_replace.csv"
    # 出力ファイルの初期化（削除）
    if os.path.exists(output_file):
        os.remove(output_file)

    f_label = open(label_file, "a",newline='')
    label_writer = csv.writer(f_label)
    with open(input_file, "r") as f_in:
        # csv_reader = csv.reader(f_in, delimiter=",",)
        csv_reader = csv.reader(f_in, delimiter=",", quotechar='"',quoting = csv.QUOTE_ALL)
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

# 学習用データCSVファイルに追記
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



if __name__ == "__main__":    
    target_dir = "./../../mlfile/csv/"
    os.makedirs(target_dir, exist_ok=True) # 結果を出力するフォルダ(pathで指定)が存在しなければ新規作成
    # 重複防止の為、以前取得したcsvファイルを削除
    file_list = glob.glob(target_dir + "*.csv")
    for file in file_list:
        os.remove(file)
    # shutil.rmtree(target_dir)
    # os.mkdir(target_dir)

    # os.system("mongoimport -d nm4bd -c csvtest --headerline --columnsHaveTypes --type=csv ../../working/exp_param_0611.csv --drop")
    # common_id_list = ["161207_0", "161208_0"]  # 日を跨いだ時
    # common_id_list = ["190611_","190617_"]  # 0611: Node前、0617: 中点
    ### TODO: 日程と最大クエリ数を指定
    common_id_list = ["190617_"]
    Num_of_query = 108 #全queryの数
    for common_id in common_id_list:
        for id_num in range(1,Num_of_query):
            id_str = common_id + ("00" + str(id_num))[-3:]
            if db.csvtest.find_one({"exp_id":id_str}) is not None:
                exp_info = db.csvtest.find_one({"exp_id":id_str})
                print("\n=== " + id_str + " ===")

                ### floor_numは1桁のみ!  ###
                floor = exp_info["floor"]
                # if floor == "W2-8F":
                #     continue
                floor_num = floor[3:4]
                ##########################
                print(exp_info)
                # 実験データ一回分まとめ
                make_dbmlog(exp_info)

                tmp_file_name = './../../mlfile/csv/tmp_' + id_str +'.csv'
                out_file_name = target_dir + id_str +'.csv'
                label_file = target_dir + common_id + floor +'_label.csv'
                train_file = target_dir + common_id + floor +'_train.csv'
                command = 'mongoexport --sort {"datetime":1} -d nm4bd -c dbmlog -o '+ tmp_file_name +' --csv --fieldFile ./../../mlfile/txt/dbm_field'+ floor_num +'.txt'

                # RSSIデータCSV出力
                os.system(command)

                # 1行目削除
                with open(tmp_file_name, 'r') as f:
                    doc = [row for row in csv.reader(f, delimiter='\t')]
                del doc[0]

                with open(out_file_name, 'w') as f:
                    w = csv.writer(f, delimiter='\t', lineterminator='\n')  #列区切りと行区切りの文字を指定
                    w.writerows(doc)

                os.remove(tmp_file_name)
                # 1行目削除 & 教師学習用正解ラベルデータ作成
                replace_and_make_label(out_file_name, label_file, str(exp_info["st_node"]))

                # trainデータ作成
                append_train(out_file_name, train_file)