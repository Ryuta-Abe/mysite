# -*- coding: utf-8 -*-
import time
all_st =time.time()
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
    datas = db.trtmp.find()
    for data in datas:
        data["dt_end05"] = data["get_time_no"]
        db.trtmp.save(data)

    # st_dt  = dt_from_iso_to_str(st_dt)
    tmp_st = st_dt

    while(tmp_st < ed_dt):
        loop_st = time.time()
        after_5s = shift_seconds(tmp_st, 5)
        iso_st = tmp_st
        iso_ed = after_5s

        ### execute following all process ###
        aggregate_mod(iso_st, iso_ed)
        aggregate_raw100(iso_ed)
        get_start_end_mod(iso_st)
        tmp_st = after_5s
        #####################################
        # print(time.time()-loop_st)


if __name__ == "__main__":

    param = sys.argv
    st_dt = dt_from_14digits_to_iso(str(param[1]))
    ed_dt = dt_from_14digits_to_iso(str(param[2]))
    analyze_mod(st_dt, ed_dt)
    print("total:"+str(time.time()-all_st))
