import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
from pymongo import *
client = MongoClient()
db = client.nm4bd
from sklearn import svm
from sklearn.externals import joblib
from sklearn.model_selection import cross_val_score,StratifiedShuffleSplit, GridSearchCV

from get_csi import get_csi

FLOOR = "W2-7F"
C =  10.0
gamma = 0.0007

def get_best_param():
	FLOOR = "W2-7F"
	parameters = {"kernel":"rbf","C":np.linspace(10,100,10), "gamma": np.linspace(0.0001,0.001,10)}
	parameters = [
		{'C': [1, 10, 100, 1000], 'kernel': ['linear']},
    {'C': [1, 10, 100, 1000],"gamma": [0.0001,0.001,0.01],'kernel': ['rbf']}]
	print("PARAMs to be evaluated:",parameters)
	path = "../../working/"
	X = np.genfromtxt(path + "190611_" +  + "_" + 'train.csv', delimiter = ',')
	y = np.genfromtxt(path + "190611_" +  + "_" + 'label.csv', delimiter = ',')
	if CONTAINS_MIDPOINT:
		X = np.genfromtxt(path +  + "_" + 'train.csv', delimiter = ',')
		y = np.genfromtxt(path +  + "_" + 'label.csv', delimiter = ',')
		le = preprocessing.LabelEncoder()
		le.fit(y)
		y = le.transform(y)
	clf = GridSearchCV(svm.SVC(), parameters, cv = 5,n_jobs=6)
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


def make_csi_model():
    train_list = []
    label_list = []

    RP_list = [node["pcwl_id"] for node in db.reg_pcwlnode.find({"":})]
    for RP in RP_list:
        path = "../../working/CSI/" + str(RP) + "/"
        csi = get_csi(path)
        if csi is None:
            continue
        train_list.extend(csi)
        label_list.extend([RP]*len(train_list))
    print(train_list, label_list)
    clf = svm.SVC(C = C, gamma = gamma, probability = True)
    clf.fit(train_list, label_list)
    # calc. accuracy of the model
    cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)
    scores = cross_val_score(clf, X, y, cv=cv)
    # print( + ":" + str (param[]))
    print(scores)
    # scores.std() * 2 要調査
    print("Accuracy: %0.5f (+/- %0.5f)" % (scores.mean(), scores.std() * 2))
    print("\n")
    
    # output model
    ML_FILE_PATH = "../../mlmodel/"
    # joblib.dump(clf, path +  + "_model.pkl")
    # if CONTAINS_MIDPOINT:
    # 	with open(path +  + '_label.p', 'wb') as f:  # Label encoding用のファイルを保存
    # 		pickle.dump(le, f)
    joblib.dump(clf, ML_FILE_PATH +  + "_model.pkl")
    if CONTAINS_MIDPOINT:
        with open(ML_FILE_PATH +  + '_label.p', 'wb') as f:  # Label encoding用のファイルを保存
            pickle.dump(le, f)

if __name__ == "__main__":
    make_csi_model()
    
