# -*- coding: utf-8 -*-
# import time
# st = time.time()
### classification sample
import numpy as np
from sklearn import svm
from sklearn.externals import joblib
from sklearn import preprocessing
import pickle

MODEL_DIR = "../../mlmodel/"
# IS_REGULAR = True
# MODEL_DIR = "/home/murakami2/mlmodel/"

def classify(floor, rssi_list,is_regular):
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
    if is_regular:
        for desc_index in desc_indexes:
            label = clf.classes_[desc_index]
            label_list.append(label)
    else:
        with open(MODEL_DIR + floor + "_label.p", 'rb') as f:
            le = pickle.load(f)
            label_list = le.inverse_transform(desc_indexes)

    # return (desc_indexes,clf.classes_)
    return desc_indexes, label_list

if __name__ == "__main__":
    rssi_list = [-36,-61,-58,-86,-99,-99,-32,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-92,-99,-99,-99,-99,-99]
    desc_indexes,label_list = classify("W2-7F",rssi_list)
    print(desc_indexes)
    # label_list = []
    # for desc_index in desc_indexes:
    #     label = classes[desc_index]
    #     label_list.append(label)
    print(label_list)


    