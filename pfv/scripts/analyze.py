# -*- coding: utf-8 -*-
import time
st = time.time()
import sys
from convert_datetime import *
from aggregate import *
from get_start_end import get_start_end_mod

from pymongo import *
client = MongoClient()
db = client.nm4bd

if __name__ == "__main__":

    param = sys.argv
    st_dt = str(param[1])
    ed_dt = str(param[2])
    
    datas = db.trtmp.find()
    for data in datas:
        data["dt_end05"] = int(dt_end_to_05(data["get_time_no"]))
        db.trtmp.save(data)

    tmp_st = dt_end_to_05(st_dt)
    tmp_st = dt_from_14digits_to_iso(tmp_st)
    ed_dt  = dt_from_14digits_to_iso(ed_dt)

    while(tmp_st < ed_dt):
        after_5s = shift_seconds(tmp_st, 5)
        int_st = int(dt_from_iso_to_str(tmp_st)[:14])
        int_ed = int(dt_from_iso_to_str(after_5s)[:14])

        aggregate_mod(int_st, int_ed, False, False, True)
        get_start_end_mod(False, True)
        tmp_st = after_5s


ed = time.time()
print(ed-st)