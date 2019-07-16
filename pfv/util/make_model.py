# -*- coding: utf-8 -*-
import time
st = time.time()
import numpy as np
from sklearn import svm
from sklearn.externals import joblib
from sklearn.model_selection import cross_val_score,StratifiedShuffleSplit, GridSearchCV
from sklearn import preprocessing
import pickle,csv

# le = preprocessing.LabelEncoder()
# result = le.fit_transform([1,2,3,"1,1,1,2","2-3","3-4"])
# print(result)

#FLOOR_LIST = ["W2-6F","W2-7F","W2-8F","W2-9F"]
# 7F　only ver.
FLOOR_LIST = ["W2-7F"]

param = {"W2-6F":{"C" : 2.0, "gamma" : 0.0009},
        #  "W2-7F":{"C" : 30.0, "gamma" : 0.0006},
         "W2-7F":{"C" : 10.0, "gamma" : 0.0007},
    	 "W2-8F":{"C" : 20.0, "gamma" : 0.0002},
		 "W2-9F":{"C" : 4.0, "gamma" : 0.0008}}
CONTAINS_MIDPOINT = True
"""
指定パラメータで分類モデル作成
評価スコア出力
"""

def get_best_param():
	floor = "W2-7F"
	parameters = {"kernel":"rbf","C":np.linspace(10,100,10), "gamma": np.linspace(0.0001,0.001,10)}
	parameters = [
		{'C': [1, 10, 100, 1000], 'kernel': ['linear']},
    {'C': [1, 10, 100, 1000],"gamma": [0.0001,0.001,0.01],'kernel': ['rbf']}]
	print("PARAMs to be evaluated:",parameters)
	path = "../../working/"
	X = np.genfromtxt(path + "190611_" + floor + "_" + 'train.csv', delimiter = ',')
	y = np.genfromtxt(path + "190611_" + floor + "_" + 'label.csv', delimiter = ',')
	if CONTAINS_MIDPOINT:
		X = np.genfromtxt(path + floor + "_" + 'train.csv', delimiter = ',')
		y = np.genfromtxt(path + floor + "_" + 'label.csv', delimiter = ',')
		le = preprocessing.LabelEncoder()
		le.fit(y)
		y = le.transform(y)
	clf = GridSearchCV(svm.SVC(), parameters, cv = 5,n_jobs=-2)
	clf.fit(X,y)
	params = clf.cv_results_["params"]
	ranks = clf.cv_results_["rank_test_score"]
	scores = clf.cv_results_["mean_test_score"]
	stds = clf.cv_results_["std_test_score"]
	result_list = []
	for i,param in enumerate(params):
		result = {"param":param,"rank":ranks[i],"score":scores[i]}
		result_list.append(result)
	sorted_result_list = sorted(result_list,key=lambda x:x["score"],reverse=True)
	print(sorted_result_list)
	with open('param result.csv', 'w') as f:
		writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく
		writer.writerow([result["param"] for result in sorted_result_list])    # list（1次元配列）の場合
		writer.writerow([result["rank"] for result in sorted_result_list]) 
		writer.writerow([result["score"] for result in sorted_result_list]) 
		# writer.writerows(array2d) # 2次元配列も書き込める


	best_param = clf.best_params_
	print("best_param:",best_param)
	return clf.best_params_

def make_model():

	for floor in FLOOR_LIST:
		path = "../../working/"

		X = np.genfromtxt(path + "190611_" + floor + "_" + 'train.csv', delimiter = ',')
		y = np.genfromtxt(path + "190611_" + floor + "_" + 'label.csv', delimiter = ',')
		# print(y)
		# le = preprocessing.LabelEncoder()
		# le.fit(y)
		# y = le.transform(y)
		# print(y)
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
		# with open(path + floor + '_label.p', 'wb') as f:
		# 	pickle.dump(le, f)

	print("Time to make model", end=":")
	print(time.time()-st)

"""
MEMO:
LabelEncoderの保存法
pickle.dump(le, 'foo.txt')
with open('foo.p', 'wb') as f:
  pickle.dump(le, f)
with open('foo.p', 'rb') as f:
  le2 = pickle.load(f)

le2.inverse_transform([2, 1, 0, 2, 3, 1])
  #=> array(['tokyo', 'osaka', 'nagoya', 'tokyo', 'yokohama', 'osaka'], dtype='<U8')
"""

if __name__ == "__main__":
	st = time.time()
	get_best_param()
	ed = time.time()
	print("Time to find best param:", ed-st)
