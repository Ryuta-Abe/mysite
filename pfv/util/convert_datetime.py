# -*- coding: utf-8 -*-
import datetime

# 今日の日付
d = datetime.datetime.today() # 2014-11-20 19:41:51.011593
d = str(d.year)+("0"+str(d.month))[-2:]+("0"+str(d.day))[-2:]+("0"+str(d.hour))[-2:]+("0"+str(int(d.minute/5)*5))[-2:] # 201411201940

# 分まで
# 201411201940(str) --> 2014-11-20 19:40(str)
def datetime_to_12digits(date_time = d):
  if (len(date_time) >= 12):
    date_time = date_time[0:12]
  else:
    l = 12 - len(date_time) # lは不足分
    for i in (0,l):
      date_time += "0"

  date_time = dt_insert_partition_to_min(date_time)
  return date_time

# 分まで
# str形式(201411220123) --> str形式(2014-11-22 01:23)
def dt_insert_partition_to_min(dt):
    dt = dt[0:4]+"-"+dt[4:6]+"-"+dt[6:8]+" "+dt[8:10]+":"+dt[10:12]
    return dt

# 少数第3位まで対応可
# str形式(2014-04-05 12:34:56.789) --> isodate形式
def dt_from_str_to_iso(dt):
    from datetime import datetime
    dt = str(dt[0:4])+"-"+str("0"+dt[5:7])[-2:]+"-"+str("0"+dt[8:10])[-2:]+" "+str("00"+dt[11:13])[-2:]+":"+str("00"+dt[14:16])[-2:]+":"+str("00"+dt[17:19])[-2:]+"."+str("000"+dt[20:23])[-3:]
    dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f')
    return dt

# 秒まで
# 20141120194030(str) --> isodate形式
def dt_from_14digits_to_iso(dt):
  from datetime import datetime
  dt = str(dt)
  dt = str(dt[0:4])+"-"+str("0"+dt[4:6])[-2:]+"-"+str("0"+dt[6:8])[-2:]+" "+str("00"+dt[8:10])[-2:]+":"+str("00"+dt[10:12])[-2:]+":"+str("00"+dt[12:14])[-2:]
  dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
  return dt

# 少数第3位まで対応可
# isodate形式 --> str形式(20140405123456789)
def dt_from_iso_to_str(dt):
    dt = str(dt.year)+("0"+str(dt.month))[-2:]+("0"+str(dt.day))[-2:]+("0"+str(dt.hour))[-2:]+("0"+str(dt.minute))[-2:]+("00"+str(dt.second))[-2:]+("000"+str(dt.microsecond))[-2:]
    return dt

# jap表記へ 秒まで必要
def dt_from_iso_to_jap(dt):
    dt = str(dt.year)+"年"+("0"+str(dt.month))[-2:]+"月"+("0"+str(dt.day))[-2:]+"日 "+("0"+str(dt.hour))[-2:]+":"+("0"+str(dt.minute))[-2:]+":"+("0"+str(dt.second))[-2:]
    return dt

# isodate形式 --> numlong形式(20140405123456789)
def dt_from_iso_to_numlong(dt):
    dt = int(dt_from_iso_to_str(dt))
    return dt

# isodate形式 + int(+ or -) --> 指定時刻分ずらしたisodate形式
def shift_seconds(dt, second):
    import datetime
    dt = dt + datetime.timedelta(seconds = second)
    return dt

def shift_minutes(dt, minute):
    import datetime
    dt = dt + datetime.timedelta(minutes = minute)
    return dt

def shift_hours(dt, hour):
    import datetime
    dt = dt + datetime.timedelta(hours = hour)
    return dt

# input : int or str datetime
def dt_end_to_05(dt):
    dt = str(dt)[0:14]
    dt_end = int(dt[-1:])

    if (0 <= dt_end <=4):
      dt = str(dt[0:13]) + "0"
    elif (5 <= dt_end <=9):
      dt = str(dt[0:13]) + "5"

    return dt

def str_to_next05_str(dt,input_type,output_type):
    dt = str(dt)[0:14]
    dt_end = int(dt[-1])

    if (1 <= dt_end <= 4):
      dt = dt[0:13] + "5"
    elif (6 <= dt_end <= 9):
      dt_end2 = int(dt[-2])
      dt_end2 += 1 
      dt = dt[0:12] + str(dt_end2) +  "5"

    return dt
  
# input: dtはstr,isoのいずれでも可
# output: output_typeで指定した型（"str"か"iso"）
def dt_to_end_next05(dt,output_type):
  import datetime
  dt_end = 0

  if output_type != "str" and output_type != "iso":
    print("the argument num 2 must be str or datetime.datetime!")
  
  if isinstance(dt,datetime.datetime):
    dt_end = int(dt_from_iso_to_str(dt)[13])  
  elif isinstance(dt,str):
    dt_end = int(dt[13])
    dt = dt_from_14digits_to_iso(dt)
  else:
    print("the type of the argument num 1 must be str or datetime.datetime!")

  if (1 <= dt_end <= 4):
    delta = 5 - dt_end
    dt = shift_seconds(dt,delta)
  elif (6 <= dt_end <= 9):
    delta = 10 - dt_end
    dt = shift_seconds(dt,delta)

  if output_type == "str":
    dt = dt_from_iso_to_str(dt)[:14]

  return dt 

# input:isodate, output:isodate(end 0or5)
def iso_to_end05iso(dt):
    dt = dt_from_iso_to_str(dt)
    dt = dt_end_to_05(dt)
    dt = dt_from_14digits_to_iso(dt)
    return dt