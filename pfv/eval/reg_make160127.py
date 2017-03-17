# -*- coding: utf-8 -*-
import time
st = time.time()
import matplotlib.pyplot as plt
from matplotlib.ticker import *

### classification sample
import numpy as np
from sklearn import svm, linear_model
from sklearn.externals import joblib
from sklearn.neural_network import MLPRegressor
print("mod_import:"+str(time.time()-st))

floor_list = ["W2-6F","W2-7F","W2-8F","W2-9F"]

# 回帰分析モデルのパラメータ
activation_list = ["relu"]
solver_list = ["adam"]
prm_list = []

for act in activation_list:
    for solver in solver_list:
        prm_list.append([act,solver])

# 各フロアの"回帰"モデル作成
for floor in floor_list:
    for prm in prm_list:
        # make model
        trainFeature = np.genfromtxt(floor+'_train.csv', delimiter = ',')
        trainLabel = np.genfromtxt(floor+'_reglabel.csv', delimiter = ',')
        # clf = linear_model.LinearRegression(normalize=True)
        clf = MLPRegressor(activation=prm[0], solver=prm[1])
        title = prm[0] +"_"+ prm[1]
        clf.fit(trainFeature, trainLabel)

        # # # export model
        joblib.dump(clf, floor+'_regmodel.pkl') 
