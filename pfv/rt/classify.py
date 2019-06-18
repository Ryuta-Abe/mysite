# -*- coding: utf-8 -*-
# import time
# st = time.time()
### classification sample
import numpy as np
from sklearn import svm
from sklearn.externals import joblib

MODEL_DIR = "../../mlmodel/"
# MODEL_DIR = "/home/murakami2/mlmodel/"

def classify(floor, rssi_list):
    # import model
    clf = joblib.load(MODEL_DIR+floor+"_model.pkl") 

    # testFeature = np.genfromtxt('test_1213.csv', delimiter = ',') 
    tmp = rssi_list
    testFeature = np.array(tmp).reshape((1, -1))
    # testFeature = scaler.transform(tmp)

    result = clf.predict_proba(testFeature)[0]
    print(result)
    desc_indexes = result.argsort()[::-1]
    # print(desc_indexes)
    # for data in result:
    #     data = int(data)
    #print(clf.classes_)
    # print(result)
    for i in range(3):
        print(str(i+1) + "th: " + str(desc_indexes[i]))
        label = clf.classes_[desc_indexes[i]]
        print(label)
    return (desc_indexes,clf.classes_)

if __name__ == "__main__":
    rssi_list = [-36,-61,-58,-86,-99,-99,-32,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-92,-99,-99,-99,-99,-99]
    desc_indexes = classify("W2-7F",rssi_list)
    print(desc_indexes)


    