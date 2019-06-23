# -*- coding: utf-8 -*-
import datetime
import pymongo

# mac情報付きpfvinfo
def make_pfvmacinfo(flow_list,db_name,min_interval):  # TODO: intervalを超える時間での分析（補完対応）

    progress = 0
    for data in flow_list:
        if data == None:
            continue
        #tlist = db.pcwltime.find({"datetime":{"$gt":data["start_time"]}}).sort("datetime", ASCENDING).limit(num)
        route_info = db.idealpcwlroute.find_one({"$and": [{"floor" : data["floor"]},
                                                    {"query" : data["start_node"][0]["pcwl_id"]}, 
                                                    {"query" : data["end_node"][0]["pcwl_id"]} ])


        tmp_st_ed_info = []
        for node in route["route"]:
            tmp_st_ed_info.append(node["direction"])
        st_ed_info = [tmp_st_ed_info]

        # 人流情報or滞留情報の登録
        location = data["start_node"][0]["pcwl_id"] # 現在位置の情報
        for j in range(0,num):
                new_data = {"datetime":tlist[j]["datetime"],"mac":data["mac"],"route":st_ed_info[j],"floor":data["floor"]}
                db.pfvmacinfo.insert(new_data)
                location = st_ed_info[j][-1][-1]

        progress += 1
        if ((progress % 1000) == 0) or (progress == len(flow_list)):  # 1000件のデータを処理するまたは、
            print("pfvmacinfo "+str(progress)+" / "+str(len(flow_list))+" ("+str(round(progress/len(dataset)*100,1))+"%)")