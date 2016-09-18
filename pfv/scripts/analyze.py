# -*- coding: utf-8 -*-
import time
import sys
from convert_datetime import *
from aggregate import *
from get_start_end import get_start_end_mod
from aggregate_raw100 import aggregate_raw100

from pymongo import *
client = MongoClient()
db = client.nm4bd

# input:iso datetime
def analyze_mod(st_dt, ed_dt):
    # print("st:"+str(st_dt))
    # print("ed:"+str(ed_dt))
    datas = db.trtmp.find()
    for data in datas:
        data["dt_end05"] = data["get_time_no"]
        db.trtmp.save(data)
        # print(data)

    st_dt  = dt_from_iso_to_str(st_dt)
    # tmp_st = dt_end_to_05(st_dt)
    tmp_st = dt_from_14digits_to_iso(st_dt)
    tmp_ed  = dt_from_iso_to_str(ed_dt)
    ed_dt  = dt_from_14digits_to_iso(tmp_ed)

    # print("st:"+str(tmp_st))
    # print("ed:"+str(ed_dt))
    while(tmp_st < ed_dt):
        # print(str(tmp_st)+" < "+str(ed_dt))
        after_5s = shift_seconds(tmp_st, 5)
        # int_st = int(dt_from_iso_to_str(tmp_st)[:14])
        # int_ed = int(dt_from_iso_to_str(after_5s)[:14])
        int_st = tmp_st
        int_ed = after_5s

        ### execute following all process ###
        # print("st:"+str(int_st))
        # print("ed:"+str(int_ed))

        aggregate_mod(int_st, int_ed, False, False, True)
        # aggregate_raw100(int_ed)
        get_start_end_mod(False, True)
        tmp_st = after_5s
        #####################################


if __name__ == "__main__":

    param = sys.argv
    st_dt = str(param[1])
    ed_dt = str(param[2])
    analyze_mod(st_dt, ed_dt)
    

