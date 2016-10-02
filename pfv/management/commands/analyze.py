# -*- coding: utf-8 -*-
import time
all_st = time.time()
from django.core.management.base import BaseCommand

# from pfv.scripts.convert_datetime import *
# from pfv.scripts.aggregate import *
# from pfv.scripts.get_start_end import get_start_end_mod
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../scripts')
# print(sys.path)

from convert_datetime import *  
from aggregate import *
from get_start_end import get_start_end_mod
from aggregate_raw100 import aggregate_raw100

from pymongo import *
client = MongoClient()
db = client.nm4bd

class Command(BaseCommand):
    args = '<st_dt[int14digits] ed_dt[int14digits]>'
    help = u'analyze data : aggregate->get_start_end->save'

    def handle(self, *args, **options):
        st_dt = dt_from_14digits_to_iso(str(args[0]))
        ed_dt = dt_from_14digits_to_iso(str(args[1]))
        
        datas = db.trtmp.find()
        for data in datas:
            data["dt_end05"] = data["get_time_no"]
            db.trtmp.save(data)

        st_dt  = dt_from_iso_to_str(st_dt)
        tmp_st = dt_from_14digits_to_iso(st_dt)
        tmp_ed = dt_from_iso_to_str(ed_dt)
        ed_dt  = dt_from_14digits_to_iso(tmp_ed)

        while(tmp_st < ed_dt):
            loop_st = time.time()
            after_5s = shift_seconds(tmp_st, 5)
            iso_st = tmp_st
            iso_ed = after_5s

            ### execute following all process ###
            aggregate_mod(iso_st, iso_ed, False, False, True)
            aggregate_raw100(iso_ed)
            get_start_end_mod(iso_st, False, True)
            tmp_st = after_5s
            #####################################
            # print(time.time()-loop_st)

        print("total:"+str(time.time()-all_st))
