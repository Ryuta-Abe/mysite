# -*- coding: utf-8 -*-
import time
st = time.time()
import numpy as np
from sklearn import svm
from sklearn.externals import joblib
from sklearn.model_selection import cross_val_score,StratifiedShuffleSplit

#FLOOR_LIST = ["W2-6F","W2-7F","W2-8F","W2-9F"]
# 7F　only ver.
FLOOR_LIST = ["W2-7F"]

param = {"W2-6F":{"C" : 2.0, "gamma" : 0.0009},
		 "W2-7F":{"C" : 30.0, "gamma" : 0.0006},
    	 "W2-8F":{"C" : 20.0, "gamma" : 0.0002},
		 "W2-9F":{"C" : 4.0, "gamma" : 0.0008}}

"""
指定パラメータで分類モデル作成
評価スコア出力
"""
for floor in FLOOR_LIST:
	path = "../../working/"

	X = np.genfromtxt(path + floor + "_" + 'train.csv', delimiter = ',')
	y = np.genfromtxt(path + floor + "_" + 'label.csv', delimiter = ',')
	clf = svm.SVC(C = param[floor]["C"], gamma = param[floor]["gamma"],probability = True)
	clf.fit(X,y)

	# calc. accuracy of the model
	cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)
	scores = cross_val_score(clf, X, y, cv=cv)
	print(floor + ":" + str (param[floor]))
	print(scores)
    # scores.std() * 2 要調査
	print("Accuracy: %0.5f (+/- %0.5f)" % (scores.mean(), scores.std() * 2))
	print("\n")
	
	# output model
	joblib.dump(clf, path + floor + "_model.pkl")

print("Time to make model", end=":")
print(time.time()-st)