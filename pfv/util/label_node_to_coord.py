# -*- coding: utf-8 -*-
import csv
from pymongo import *
client = MongoClient()
db = client.nm4bd
floor_list =["W2-6F","W2-7F","W2-8F","W2-9F"]
# floor_list =["W2-9F"]


"""
学習用ラベルデータのAP番号を座標に変換したCSVを出力する[回帰分析用]
"""
for floor in floor_list:
    csv_reader = csv.reader(open("C:/Users/Ryuta/Desktop/sklearn/"+floor+"_label.csv", "r"), delimiter=",", quotechar='"')
    csv_writer = csv.writer(open("C:/Users/Ryuta/Desktop/sklearn/"+floor+"_reglabel.csv", 'w',newline=''))

    datas = []
    for row in csv_reader:
        pcwl_id = int(row[0])
        node_info = db.reg_pcwlnode.find_one({"floor":floor,"pcwl_id":pcwl_id})
        if node_info != None:
            pos_row = [node_info["pos_x"], node_info["pos_y"]]
            datas.append(pos_row)
            # print(pos_row)
        else:
            print("=== Invalid input error! ===")

    csv_writer.writerows(datas)
