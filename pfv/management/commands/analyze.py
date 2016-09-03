# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from pfv.convert_datetime import *
from pfv.aggregate import *
from pfv.get_start_end import get_start_end, get_start_end_mod


class Command(BaseCommand):
  args = '<st_dt[int14digits] ed_dt[int14digits]>'
  help = u'analyze data : aggregate->get_start_end->save'

  def handle(self, *args, **options):
    st_dt = str(args[0])
    st_dt_end = int(str(st_dt)[-1:])
    if (0 <= st_dt_end <=4):
      tmp_st = str(st_dt[0:13]) + "0"
    elif (5 <= st_dt_end <=9):
      tmp_st = str(st_dt[0:13]) + "5"


    # dt05
    datas = db.trtmp.find()
    for data in datas:
      dt_end = int(str(data["get_time_no"])[-1:])
      if (0 <= dt_end <=4):
        data["dt_end05"] = int(str(data["get_time_no"])[0:13] + "0")
      elif (5 <= dt_end <=9):
        data["dt_end05"] = int(str(data["get_time_no"])[0:13] + "5")
      db.trtmp.save(data)
      

    tmp_st = dt_from_14digits_to_iso(tmp_st)
    ed_dt    = dt_from_14digits_to_iso(str(args[1]))

    while(tmp_st < ed_dt):
      after_5s = shift_seconds(tmp_st, 5)
      int_st = int(dt_from_iso_to_str(tmp_st)[:14])
      int_ed = int(dt_from_iso_to_str(after_5s)[:14])

      aggregate_mod(int_st, int_ed, False, False, True)
      get_start_end_mod(False, True)
      # print(tmp_st)
      tmp_st = after_5s

    print("django test")
