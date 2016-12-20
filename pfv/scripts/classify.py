# -*- coding: utf-8 -*-
# import time
# st = time.time()
### classification sample
import numpy as np
from sklearn import svm
from sklearn.externals import joblib

# MODEL_DIR = "C:/Users/Ryuta/Desktop/sklearn/"
MODEL_DIR = "/home/murakami2/mlmodel/"

def classify(floor, rssi_list):
    # import model
    clf = joblib.load(MODEL_DIR+floor+"_model.pkl") 

    # testFeature = np.genfromtxt('test_1213.csv', delimiter = ',') 
    tmp = rssi_list
    testFeature = np.array(tmp).reshape((1, -1))
    # testFeature = scaler.transform(tmp)

    result = clf.predict_proba(testFeature)[0]
    # print(result)
    desc_indexes = result.argsort()[::-1]
    # print(desc_indexes)
    # for data in result:
    #     data = int(data)

    # print(result)
    return desc_indexes