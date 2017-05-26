# -*- coding: utf-8 -*-

flist = ["W2-6F","W2-7F","W2-9F"]

for floor in flist:
    for x in range(1,28):
        print('db.timeoutlog.find({"floor":"'+str(floor)+'","pcwl_id":'+str(x)+'}).count()'+"\n\n")