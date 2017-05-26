# -*- coding: utf-8 -*-

import csv
from pymongo import *
client = MongoClient()
db = client.nm4bd

"""
実験パラメータCSVのtag_idをmacアドレスに変換したCSVを出力
"""
csv_reader = csv.reader(open("C:/Users/Ryuta/Desktop/analyze_data/exp_param.csv", "r"), delimiter=",", quotechar='"')
f = open('C:/Users/Ryuta/Desktop/analyze_data/exp_param_conv.csv', 'w',newline='')
writer = csv.writer(f)

cnt = 0
datas = []
for row in csv_reader:
    if cnt != 0:
        mac_or_id = row[1]
        print(len(mac_or_id))

        if len(mac_or_id) < 4:
            mac_or_id = int(mac_or_id)
            tag_info = db.tag_id.find_one({"tag_id":mac_or_id})
            if tag_info != None:
                row[1] = tag_info["mac"]
                print(row[1])
        # writer = csv.writer(f)
    datas.append(row)
    
    cnt += 1

writer.writerows(datas)
f.close()
