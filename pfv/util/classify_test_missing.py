# -*- coding: utf-8 -*-
import time
st = time.time()

# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

# init DB
# db.pred_miss.drop()

### classification sample
import numpy as np
from sklearn import svm
from sklearn.externals import joblib

# must underscore
common_exp_id = "170127_"
st_exp_id = 1
ed_exp_id = 6

# data path
csv_dir = "C:/Users/Ryuta/csv/"
model_dir = "C:/Users/Ryuta/Desktop/sklearn/"

def calc_accuracy(correct_node, total_cnt, predict_list):
    correct_cnt = 0
    for pre_node in predict_list:
        pre_node_num = int(pre_node)
        if pre_node_num == correct_node:
            correct_cnt += 1

    accuracy = correct_cnt / total_cnt * 100
    print(accuracy)
    return accuracy

"""
最近隣ノードのRSSIが欠落(-99dbm)した場合の分類精度の評価
"""
if __name__ == '__main__':
    query_list = []
    for i in range(st_exp_id,ed_exp_id + 1):
        exp_num = ("000" + str(i))[-3:]
        exp_id  = common_exp_id + exp_num
        query = {"exp_id" : exp_id}

        exp_info = db.csvtest.find_one(query)

        clf = joblib.load(model_dir + exp_info["floor"] +'_model.pkl')

        if exp_info == None:
            continue
        else:
            print(exp_info)
            floor_node_list = []
            floor_node_col = db.pcwlnode.find({"floor":exp_info["floor"]}).sort("pcwl_id",ASCENDING)
            correct_node = exp_info["st_node"]
            for node in floor_node_col:
                floor_node_list.append(node["pcwl_id"])

            index = floor_node_list.index(correct_node)
            print(index)

            testFeature = np.genfromtxt(csv_dir + exp_id + '.csv', delimiter = ',')
            total_cnt = len(testFeature)

            if total_cnt == 0:
                continue

            result_org = clf.predict(testFeature)
            print(result_org)
            org_accuracy = calc_accuracy(correct_node, total_cnt, result_org)

            for line in testFeature:
                line[index] = -99

            result_missing = clf.predict(testFeature)
            print(result_missing)
            missing_accuracy = calc_accuracy(correct_node, total_cnt, result_missing)

        ins_data = {"exp_id":exp_id, "floor":exp_info["floor"], "pcwl_id":exp_info["st_node"],
                    "org_rate":org_accuracy, "missing_accuracy":missing_accuracy}
        db.pred_miss.insert(ins_data)

