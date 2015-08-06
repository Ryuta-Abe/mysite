import datetime

# 今日の日付
d = datetime.datetime.today() # 2014-11-20 19:41:51.011593
d = str(d.year)+("0"+str(d.month))[-2:]+("0"+str(d.day))[-2:]+("0"+str(d.hour))[-2:]+("0"+str(int(d.minute/5)*5))[-2:] # 201411201940


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


# str形式(201411220123) --> str形式(2014-11-22 01:23)
def dt_insert_partition_to_min(dt):

	dt = dt[0:4]+"-"+dt[4:6]+"-"+dt[6:8]+" "+dt[8:10]+":"+dt[10:12]

	return dt


# str形式(2014-04-05 12:34:56.789) --> isodate形式
def dt_from_str_to_iso(dt):

	from datetime import datetime

	dt = str(dt[0:4])+"-"+str("0"+dt[5:7])[-2:]+"-"+str("0"+dt[8:10])[-2:]+" "+str("00"+dt[11:13])[-2:]+":"+str("00"+dt[14:16])[-2:]+":"+str("00"+dt[17:19])[-2:]+"."+str("000"+dt[20:23])[-3:]
	dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f')
	return dt


# isodate形式 --> str形式(20140405123456789)
def dt_from_iso_to_str(dt):

	dt = str(dt.year)+("0"+str(dt.month))[-2:]+("0"+str(dt.day))[-2:]+("0"+str(dt.hour))[-2:]+("0"+str(dt.minute))[-2:]+("00"+str(dt.second))[-2:]+("000"+str(dt.microsecond))[-2:]
	return dt


def dt_from_iso_to_jap(dt):
	dt = str(dt.year)+"年"+("0"+str(dt.month))[-2:]+"月"+("0"+str(dt.day))[-2:]+"日 "+("0"+str(dt.hour))[-2:]+":"+("0"+str(dt.minute))[-2:]+":"+("0"+str(dt.second))[-2:]
	return dt


# isodate形式 --> 指定時刻分ずらしたisodate形式
def shift_time(dt):
	import datetime

	dt = dt - datetime.timedelta(seconds = 2)
	return dt

