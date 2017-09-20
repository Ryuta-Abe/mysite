# import Env
import os, sys
from collections import Counter
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from convert_datetime import dt_from_14digits_to_iso
from pymongo import *
client = MongoClient()
db = client.nm4bd

def remake_data(st,ed):
    # 該当期間に更新されたmacの取り出し
    # maclist = ["00:11:81:10:01:00"]
    maclist = []
    maclist += db.pastdata.find({},{"mac":1,"_id":0})

    for mac in maclist:
        mac = mac["mac"]
        # 対象macの移動・滞留データの取り出し
        data = []
        data += db.pfvmacinfo.find({"$and":[{"datetime":{"$gte":st,"$lte":ed}},{"mac":mac}]},{"_id":0})
        data += db.staymacinfo.find({"$and":[{"datetime":{"$gte":st,"$lte":ed}},{"mac":mac}]},{"_id":0})
        # 取り出したデータを時刻順にソート
        keyfunc_time = lambda x:x["datetime"]
        data = sorted(data,key=keyfunc_time)

        update_dt = 0 # 最終更新時刻
        ap_list_flow =[] # 1データ分のAPのリスト
        ap_list_stay = []
        flow_cnt = 0 # 移動数カウント
        stay_cnt = 0 # 滞留数カウント
        pre_floor = 0 # 前の時刻ののフロア
        for time in data:
            if update_dt==0:
                start_dt = time["datetime"]
            else:
                if ((time["datetime"] - update_dt).seconds >30) or (time["floor"] != pre_floor):
                    print_result(mac,start_dt,update_dt,ap_list_flow,ap_list_stay,flow_cnt,stay_cnt,pre_floor)
                    start_dt = time["datetime"] # 開始時刻更新
                    ap_list_flow =[] # 1データ分のAPのリスト
                    ap_list_stay = []
                    flow_cnt = 0 # 移動数カウント
                    stay_cnt = 0 # 滞留数カウント
            if "pcwl_id" in time:
                stay_cnt += 1
                ap_list_flow.append({"pcwl_id":time["pcwl_id"],"datetime":time["datetime"]})
                ap_list_stay.append(time["pcwl_id"])
                state = time["pcwl_id"]
            elif "route" in time:
                flow_cnt += 1
                for i in range(len(time["route"])):
                    if ap_list_flow == []:
                        ap_list_flow.append({"pcwl_id":time["route"][i][0],"datetime":time["datetime"]})
                    ap_list_flow.append({"pcwl_id":time["route"][i][1],"datetime":time["datetime"]})
                    # if i == 0:
                    #     ap_list_flow.append({"pcwl_id":time["route"][i][0],"datetime":time["datetime"]})
                    #     ap_list_flow.append({"pcwl_id":time["route"][i][1],"datetime":time["datetime"]})
                    # else:
                    #     ap_list_flow.append({"pcwl_id":time["route"][i][1],"datetime":time["datetime"]})
                # print(ap_list_flow)
                # print(time["route"])
                state = time["route"]
            update_dt = time["datetime"]
            pre_floor = time["floor"]
        print_result(mac,start_dt,update_dt,ap_list_flow,ap_list_stay,flow_cnt,stay_cnt,pre_floor)

def  print_result(mac,st,ed,flow,stay,flow_cnt,stay_cnt,floor):
    flow_ap_list = [] # 時刻を付与したAPのリスト(移動時)
    stay_ap_list = [] # 時刻を付与したAPのリスト(滞留時)
    tmp_ap_list = []
    cnt = {"pcwl_id":0,"cnt":0,"start":0}
    end_cnt = 0
    start_index = 0
    end_index = 0
    for i in flow:
        if tmp_ap_list != []:
            # now_next_id = db.pcwlnode.findOne({"$and":[{"floor":floor},"pcwl_id":i]})["next_id"]
            # pre_next_id = db.pcwlnode.findOne({"$and":[{"floor":floor},"pcwl_id":ap_list[-1]]})["next_id"]
            # for id in now_next_id:

            if (tmp_ap_list[-1]["pcwl_id"] == i["pcwl_id"]) or (cnt["pcwl_id"] == i["pcwl_id"]):
                if cnt["pcwl_id"] == 0:
                    cnt["pcwl_id"] = i["pcwl_id"]
                    cnt["start"] = i["datetime"]
                elif cnt["pcwl_id"] != i["pcwl_id"]:
                    start_index = tmp_ap_list.index({"datetime":cnt["start"],"pcwl_id":cnt["pcwl_id"]})
                    if cnt["cnt"] - end_cnt <= 6:
                        del tmp_ap_list[start_index:start_index+cnt["cnt"]-end_cnt]
                    else:
                        route = []
                        for j in tmp_ap_list[end_index:start_index]:
                            route.append(j["pcwl_id"])
                        flow_ap_list.append({"start":tmp_ap_list[end_index]["datetime"],"end":tmp_ap_list[start_index]["datetime"],"route":route})
                        end_index = start_index + cnt["cnt"] - end_cnt
                        stay_ap_list.append({"start":tmp_ap_list[start_index]["datetime"],"end":tmp_ap_list[end_index-1]["datetime"],"pcwl_id":cnt["pcwl_id"]})
                    cnt["pcwl_id"] = i["pcwl_id"]
                    cnt["start"] = i["datetime"]
                    cnt["cnt"] = 0

                    # next_id = db.pcwlnode.findOne({"$and":[{"floor":floor},"pcwl_id":i["pcwl_id"]]})["next_id"]
                cnt["cnt"] += 1
                end_cnt = 0
            elif (end_cnt > 3)and((i["datetime"] - cnt["start"]).seconds>30):
                start_index = tmp_ap_list.index({"datetime":cnt["start"],"pcwl_id":cnt["pcwl_id"]})
                if cnt["cnt"] - end_cnt <= 6:
                    del tmp_ap_list[start_index:start_index+cnt["cnt"]-end_cnt]
                else:
                    route = []
                    for j in tmp_ap_list[end_index:start_index]:
                        route.append(j["pcwl_id"])
                    # flow_ap_list.append(tmp_ap_list[end_index:start_index])
                    flow_ap_list.append({"start":tmp_ap_list[end_index]["datetime"],"end":tmp_ap_list[start_index]["datetime"],"route":route})
                    end_index = start_index + cnt["cnt"] - end_cnt
                    # stay_ap_list.append(tmp_ap_list[start_index:end_index])
                    stay_ap_list.append({"start":tmp_ap_list[start_index]["datetime"],"end":tmp_ap_list[end_index-1]["datetime"],"pcwl_id":cnt["pcwl_id"]})
                cnt = {"pcwl_id":0,"cnt":0,"start":0}
                end_cnt = 0
            elif cnt["pcwl_id"] != 0:
                    cnt["cnt"] += 1
                    end_cnt += 1
        tmp_ap_list.append({"datetime":i["datetime"],"pcwl_id":i["pcwl_id"]})
    if (flow_ap_list == [])and(stay_ap_list == [])and(stay_cnt/(stay_cnt+flow_cnt)*100 >= 70):
        # if stay_cnt/(stay_cnt+flow_cnt)*100 >= 70:
        stay_ap_list.append({"start":st,"end":ed,"pcwl_id":cnt["pcwl_id"]})
    else:
        if cnt["pcwl_id"] != 0:
            start_index = tmp_ap_list.index({"datetime":cnt["start"],"pcwl_id":cnt["pcwl_id"]})
            if cnt["cnt"] - end_cnt <= 6:
                import pdb; pdb.set_trace()  # breakpoint b715c456 //
                del tmp_ap_list[start_index:start_index+cnt["cnt"]-end_cnt]
                route = []
                for j in tmp_ap_list:
                    route.append(j["pcwl_id"])
                flow_ap_list.append({"start":tmp_ap_list[end_index]["datetime"],"end":tmp_ap_list[-1]["datetime"],"route":route})
            else:
                route = []
                for j in tmp_ap_list[end_index:start_index]:
                    route.append(j["pcwl_id"])
                flow_ap_list.append({"start":tmp_ap_list[end_index]["datetime"],"end":tmp_ap_list[start_index]["datetime"],"route":route})
                end_index = start_index + cnt["cnt"] - end_cnt
                stay_ap_list.append({"start":tmp_ap_list[start_index]["datetime"],"end":tmp_ap_list[end_index-1]["datetime"],"pcwl_id":cnt["pcwl_id"]})
        else:
            route = []
            for i in tmp_ap_list:
                route.append(i["pcwl_id"])
            flow_ap_list.append({"start":tmp_ap_list[end_index]["datetime"],"end":tmp_ap_list[-1]["datetime"],"route":route})
    tmp = Counter(stay)
    print(mac)
    print(st)
    print(ed)
    # print(flow)
    # print(tmp_ap_list)
    print("flow------------------------------------------------------------------------")
    print(flow_ap_list)
    print("stay------------------------------------------------------------------------")
    print(stay_ap_list)
    print(stay)
    # print(tmp.most_common(5))
    print("滞留割合："+str(round(stay_cnt/(stay_cnt+flow_cnt)*100,2)))
    print("AP"+str(tmp.most_common(5)[0][0])+"滞留率:"+str(round(tmp.most_common(5)[0][1]/len(stay)*100,2))+"%")
    print("----------------------------------------------------------------------------")

if __name__ == '__main__':
    st = dt_from_14digits_to_iso(20170905175000)
    ed = dt_from_14digits_to_iso(20170907180000)
    remake_data(st,ed)
