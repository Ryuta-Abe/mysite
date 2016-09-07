# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from pfv.scripts.convert_datetime import *
from pfv.scripts.aggregate import *
from pfv.scripts.get_start_end import get_start_end_mod


class Command(BaseCommand):
  args = '<st_dt[int14digits] ed_dt[int14digits]>'
  help = u'analyze data : aggregate->get_start_end->save'

  def handle(self, *args, **options):
    st_dt = str(args[0])
    ed_dt = str(args[1])
    
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
      # print(tmp_st)
      tmp_st = after_5s
