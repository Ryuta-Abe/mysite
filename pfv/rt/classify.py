# -*- coding: utf-8 -*-
# import time
# st = time.time()
### classification sample
import numpy as np
from sklearn import svm
from sklearn.externals import joblib
from sklearn import preprocessing
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
from utils import get_pcwl_index
import pickle
# TODO: scikit-learnのupdate,モデル再作成
MODEL_DIR = "../../mlmodel/"
# IS_REGULAR = True
# MODEL_DIR = "/home/murakami2/mlmodel/"

def get_deleted_rssi_list(floor,rssi_list):
    # pcwl_id_list = [2,4,6,8,9,11,24,26,21,18,16,14,13]
    # 消去対象のPCWL_id(index: 2,4,6,8,9,11,13,14,16,18,20,23,25)
    delete_id_list = [2,4,6,8,9,11,13,14,16,18,21,24,26]
    delete_index_list = get_pcwl_index(floor,delete_id_list,True)
    rssi_list = [rssi for index,rssi in enumerate(rssi_list) if not index in delete_index_list]
    return rssi_list

def classify(floor, rssi_list,CONTAINS_MIDPOINT,DELETES_AP):
    if DELETES_AP:
        rssi_list = get_deleted_rssi_list(floor,rssi_list)
    # import model
    clf = joblib.load(MODEL_DIR+floor+"_model.pkl") 
    # with open(MODEL_DIR + floor + "_label.p", 'rb') as f:
    #     le = pickle.load(f)

    # testFeature = np.genfromtxt('test_1213.csv', delimiter = ',') 
    tmp = rssi_list
    testFeature = np.array(tmp).reshape((1, -1))
    # testFeature = scaler.transform(tmp)

    result = clf.predict_proba(testFeature)[0]
    desc_indexes = result.argsort()[::-1]
    # print(desc_indexes)
    # for data in result:
    #     data = int(data)
    #print(clf.classes_)
    # print(result)
    # for i in range(3):
    #     # print(str(i+1) + "th: ",end = "")
    #     label = le.inverse_transform([desc_indexes[i]])
    #     # print("label encoder:", label)
    # # print("----------")
    label_list = []
    if CONTAINS_MIDPOINT:
        with open(MODEL_DIR + floor + "_label.p", 'rb') as f:
            le = pickle.load(f)
            label_list = le.inverse_transform(desc_indexes)

    else:
        for desc_index in desc_indexes:
            label = clf.classes_[desc_index]
            label_list.append(label)

    # return (desc_indexes,clf.classes_)
    return desc_indexes, label_list

if __name__ == "__main__":
    rssi_list = [-36,-61,-58,-86,-40,-99,-32,-90,-91,-92,-93,-94,-95,-96,-97,-98,-89,-79,-80,-81,-82,-83,-84,-85,-86,-87]
    # rssi_list = [-36,-58,-40,-32,-92,-94,-97,-89,-80,-82,-83,-85,-87]

    rssi_list = get_deleted_rssi_list("W2-7F",rssi_list)
    print(rssi_list)



    # desc_indexes,label_list = classify("W2-7F",rssi_list)
    # print(desc_indexes)
    # # label_list = []
    # # for desc_index in desc_indexes:
    # #     label = classes[desc_index]
    # #     label_list.append(label)
    # print(label_list)


    