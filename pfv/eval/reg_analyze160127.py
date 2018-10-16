# -*- coding: utf-8 -*-
import time
st = time.time()

# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from pymongo import *
from datetime import datetime
from convert_datetime import dt_to_end_next05,dt_from_14digits_to_iso,shift_seconds
from examine_route  import *
from get_coord import *
from convert_to_mac import convert_to_mac

import math
import matplotlib.pyplot as plt
from matplotlib.ticker import *

### classification sample
import numpy as np
from sklearn import svm, linear_model
from sklearn.externals import joblib
from sklearn.neural_network import MLPRegressor
print("mod_import:"+str(time.time()-st))

# 回帰分析_誤差距離
db.reg_result.drop()

query_list = []
## 実行前に指定 ##
# edgeへの垂線の足を端末の場所とする
USE_PERP = True
V_LIMIT = 75
DIST_TH = 65 #使わないときは999(適当に大きい数)にする
# FIG_SAVE_DIR = "C:/Users/Ryuta/Desktop/sklearn/perp/"
FIG_SAVE_DIR = "../../mlfile/figure/regression(fitting_past)/"
common_exp_id = "170127_"
st_exp_id = 1
ed_exp_id = 75

def rounding(num, round_place):
    rounded_num = round(num*pow(10, round_place)) / pow(10, round_place)
    return rounded_num

def make_exp_id(common_exp_id, st_exp_id, ed_exp_id):
    query_list = []
    for i in range(st_exp_id,ed_exp_id + 1):
        exp_num = ("000" + str(i))[-3:]
        exp_id  = common_exp_id + exp_num
        query = {"exp_id" : exp_id}
        query_list.append(query)
    return query_list

def csv_exam_reg_route(query_list = query_list):
    for query in query_list:
        # 解析データによる座標を作る場合は　get_analy_coord　を使う
        reg_analy_coord(query)
        # 評価のみの場合は下の行のみ実行
        # query_exam_reg_route(query)

def reg_analy_coord(query_id):
    """
    回帰分析を行う(query_idに対応するデータを解析する)
    @param  query_id:str
    """
    db.reg_analy_coord.drop()
    datas = []
    datas += db.csvtest.find(query_id)
    for data in datas:
        mac = data["mac"]
        floor = data["floor"]
        st_node = data["st_node"]
        ed_node = data["ed_node"]
        exp_id = data["exp_id"]
        
        clf = joblib.load('../../mlmodel/'+floor+'_regmodel.pkl')
        
        common_dt = str(data["common_dt"]) # 測定時刻における先頭の共通部分
        st_dt = dt_from_14digits_to_iso(common_dt + str(data["st_dt"]))
        if st_dt.second % 5 != 0:
            st_dt = shift_seconds(st_dt, 5-(st_dt.second % 5))
        tmp_dt = st_dt
        ed_dt = dt_from_14digits_to_iso(common_dt + str(data["ed_dt"]))
        ed_dt = iso_to_end05iso(ed_dt)
        print("\n== exp_id:" + str(exp_id) + " ==\nmac:" + str(mac) + "\nst:" + str(st_dt) + "\ned:" + str(ed_dt))

        testFeature = np.genfromtxt("../../mlfile/csv/" + query_id["exp_id"] + ".csv", delimiter = ',')
        result = clf.predict(testFeature)
        cnt = 0
        d = 0
        x_act_list = []
        y_act_list = []
        edge_datas = []
        edge_datas += db.floor_edge.find({"floor":floor})
        
        while (tmp_dt < ed_dt):


            if cnt != 0:
                v_limit = V_LIMIT # 移動距離制限[px]
                dist_th = DIST_TH
                tmp_x = result[cnt][0]
                tmp_y = result[cnt][1]
                x_dist = result[cnt][0] - result[cnt-1][0]
                y_dist = result[cnt][1] - result[cnt-1][1]
                tmp_d = math.sqrt(pow(x_dist,2) + pow(y_dist,2))
                
                while (tmp_d >= dist_th):
                    # 移動距離制限
                    if tmp_d > v_limit:
                        # result[cnt][0], result[cnt][1] = reduction_length(v_limit, 
                        tmp_x, tmp_y = reduction_length(v_limit, 
                                                        result[cnt][0], 
                                                        result[cnt][1], 
                                                        result[cnt-1][0], 
                                                        result[cnt-1][1])
                    # 垂線を下ろす
                    if USE_PERP:
                        # d, pos = get_perp(result[cnt][0], result[cnt][1], edge_datas)
                        tmp_d, pos = get_perp(tmp_x, tmp_y, edge_datas)
                        # result[cnt][0], result[cnt][1] = pos
                        tmp_x, tmp_y = pos
                    
                    x_dist = tmp_x - result[cnt-1][0]
                    y_dist = tmp_y - result[cnt-1][1]
                    tmp_d = math.sqrt(pow(x_dist,2) + pow(y_dist,2))
                    
                    # 移動距離制限を更に短く
                    v_limit -= 5

                    # while loop から抜け出せない場合の回避策
                    if v_limit == 0:
                        v_limit = V_LIMIT
                        dist_th += 10

                else:
                    if USE_PERP:
                        # d, pos = get_perp(result[cnt][0], result[cnt][1], edge_datas)
                        tmp_d, pos = get_perp(tmp_x, tmp_y, edge_datas)
                        # result[cnt][0], result[cnt][1] = pos
                        tmp_x, tmp_y = pos

                result[cnt][0] = tmp_x
                result[cnt][1] = tmp_y

            ins_data = {"mac":mac,
                        "floor":floor,
                        "datetime":tmp_dt,
                        "pos_x":result[cnt][0],
                        "pos_y":result[cnt][1],
                        }
            db.reg_analy_coord.insert(ins_data)
            cnt += 1

            actual_data = db.actual_position.find_one({"mac":mac, "datetime":tmp_dt})

            x_act_list.append(actual_data["pos_x"])
            y_act_list.append(actual_data["pos_y"])

            tmp_dt = shift_seconds(tmp_dt, 5)

        # 画像サイズ指定
        plt.figure(figsize=(10.475,4))
        
        x_list = []
        y_list = []
        for coords in result:
            x_list.append(coords[0])
            y_list.append(coords[1])

        # 軸設定
        plt.xlim([0,1000])
        plt.ylim([0,400])
        ax = plt.gca()
        ay = plt.gca()
        ax.xaxis.set_major_locator(MultipleLocator(50))
        ay.invert_yaxis()
        plt.grid()

        # plot error distance
        for num in range(0, len(x_act_list)):
            plt.plot([x_act_list[num], x_list[num]], [y_act_list[num], y_list[num]], 'g-', lw=2)

        # analyze position
        left = np.array(x_list)
        height = np.array(y_list)
        plt.plot(left, height, marker="o",lw=0.5)

        # actual position
        act_left = np.array(x_act_list)
        act_height = np.array(y_act_list)
        plt.plot(act_left, act_height, "r", marker="s",lw=0.5)

        # error distance analysis
        total_error = 0
        max_error_d = 0
        for num in range(0, cnt):
            error_x = abs(x_act_list[num] - x_list[num])
            error_y = abs(y_act_list[num] - y_list[num])
            error_d = math.sqrt(pow(error_x,2) + pow(error_y,2))
            total_error += error_d
            if error_d > max_error_d:
                max_error_d = error_d

        # print result
        max_error_d = rounding(max_error_d, 3)
        max_error_d_m = rounding(max_error_d *14.4/110, 3)
        avg_error_distance = rounding(total_error / cnt, 3)
        avg_error_distance_m = rounding(avg_error_distance *14.4/110, 3)
        print("avg error[px] : " + str(avg_error_distance))
        print("avg error[m]  : " + str(avg_error_distance_m))
        print("max error[px] : " + str(max_error_d))
        print("max error[m]  : " + str(max_error_d_m))

        # title, output
        ax.set_title(query_id["exp_id"]+"  avg_err_d[m]:"+str(avg_error_distance_m))
        plt.savefig(FIG_SAVE_DIR+query_id["exp_id"]+".png")
        plt.close()

        # insert error analysis result to DB
        data["avg_error_distance"] = avg_error_distance
        data["avg_error_distance_m"] = avg_error_distance_m
        data["max_error_distance"] = max_error_d
        data["max_error_distance_m"] = max_error_d_m
        del data["_id"]
        db.reg_result.insert(data)


def reduction_length(v_limit, current_x, current_y, past_x, past_y):
    """
    移動距離制限を設ける関数[辺をv_limitまで短縮する]
    @param  v_limit:float [速度制限]
    @param  current_x:float [最新のx座標]
    @param  current_y:float [y]
    @param  past_x:float [過去のx座標]
    @param  past_y:float　[y]
    @return new_x:float　　[速度制限を掛けたあとのx]
    @return new_y:float　　[速度制限を掛けたあとのy]
    """
    x_dist = current_x - past_x
    y_dist = current_y - past_y
    square_coord = math.sqrt(pow(x_dist,2) + pow(y_dist,2))
    if square_coord > v_limit:
        new_x = past_x + v_limit/square_coord * (x_dist)
        new_y = past_y + v_limit/square_coord * (y_dist)
    else:
        new_x = current_x
        new_y = current_y

    return new_x, new_y

def get_perp(current_x, current_y, edge_datas):
    """
    垂線の足の座標、長さを求める
    @param  current_x:float
    @param  current_y:float
    @param  edge_datas:list
    @return min_d:float [最小距離]
    @return min_pos:tuple -> (float, float) [最小距離になる座標]
    """
    min_d = 9999
    min_pos = (0, 0)
    p = current_x + current_y * 1j
    for edge in edge_datas:
        a = edge["edge"][0]["pos_x"] + edge["edge"][0]["pos_y"] * 1j
        b = edge["edge"][1]["pos_x"] + edge["edge"][1]["pos_y"] * 1j
        line = (a, b)
        pos, d = dotLineDist(p, line)
        pos = (pos.real, pos.imag)
        if d < min_d:
            min_d = d
            min_pos = pos
    return min_d, min_pos


# 垂線の足を求めるときに使う
# 内積
def dot(p1, p2):
    return p1.real*p2.real + p1.imag*p2.imag
# 外積
def cross(p1, p2):
    return p1.real*p2.imag - p1.imag*p2.real

# p:点(1+2j), line:直線(2+2j, 2+3j)
# 点から線分に垂線が下ろせない場合も距離が求められる
def dotLineDist(p, line):
    "line: (p1, p2)"
    a, b = line
    if dot(b-a, p-a) <= 0.0:
        return (a, abs(p-a))
    if dot(a-b, p-b) <= 0.0:
        return (b, abs(p-b))
    vec = (b-a) / abs(b-a)
    norm_vec = vec.imag - vec.real * 1j
    distance_h = cross(b-a, p-a)/abs(b-a)
    p_vec = norm_vec * distance_h
    return (p + p_vec, abs(distance_h))

# python ./reg_analyze160127.py で実行
if __name__ == '__main__':
    query_list = make_exp_id(common_exp_id, st_exp_id, ed_exp_id)
    csv_exam_reg_route(query_list)