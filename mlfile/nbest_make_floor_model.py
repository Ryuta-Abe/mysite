# -*- coding: utf-8 -*-
import time
st = time.time()
### classification sample
import numpy as np
from sklearn import svm
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
print("mod_import:"+str(time.time()-st))
floor_list = ["W2-7F"]
#floor_list = ["W2-6F","W2-7F","W2-8F","W2-9F"]

def get_score(clf, train_features, train_labels):
    X_train, X_test, y_train, y_test = train_test_split(train_features, train_labels, test_size=0.4, random_state=0)
    #X_train, X_test, y_train, y_test = cross_validation.train_test_split(train_features, train_labels, test_size=0.4, random_state=0)

    clf.fit(X_train, y_train)
    print (clf.score(X_test, y_test))

for floor in floor_list:
    # make model
    path = "csv/"
    trainFeature = np.genfromtxt(path + floor+'_train.csv', delimiter = ',')
    trainLabel = np.genfromtxt(path + floor+'_label.csv', delimiter = ',')
    clf = svm.SVC(kernel="rbf",C=1, gamma=0.0001,probability=True)
    clf.fit(trainFeature, trainLabel)

    get_score(clf, trainFeature, trainLabel)

    print(floor+" : "+str(time.time()-st))

    # # export model
    joblib.dump(clf, path +floor+'_model.pkl') 


