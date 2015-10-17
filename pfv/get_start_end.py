# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test, tmpcol
from pfv.save_pfvinfo import make_pfvinfo, make_pfvinfo_experiment
from pfv.convert_nodeid import *
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

client = MongoClient()
db = client.nm4bd
db.tmpcol.create_index([("get_time_no", DESCENDING), ("mac", ASCENDING)])

def get_start_end(request):
  from datetime import datetime
  tmp_mac     = ""
  tmp_startdt = datetime(2000, 1, 1, 0, 0, 0)
  # tmp_node_id   = 0
  data_lists = []
  count = 0
  count_all = 0

  # 6F実験で用いた端末のMACリスト
  mac_list_experiment = ["90:b6:86:52:77:2a","80:be:05:6c:6b:2b","98:e0:d9:35:92:4d","18:cf:5e:4a:3a:17","18:00:2d:62:6c:d1"]
  data_lists_experiment = []

  # datas = db.tmpcol.find({"_id.get_time_no":{"$gte":20150925173500,"$lte":20150925182000}}).limit(5000).sort("_id.get_time_no",-1).sort("_id.mac")
  datas = db.tmpcol.find().sort("_id.get_time_no",-1).sort("_id.mac").limit(10000)
  tmp_node_id = convert_nodeid(datas[0]['nodelist'][0]['node_id'])
  for data in datas:
    data['id'] = data['_id']

    if (data["id"]["mac"] == tmp_mac):
      data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
      data['nodelist'] = sorted(data['nodelist'], key=lambda x:x["dbm"], reverse=True)

      for list_data in data['nodelist']:
        list_data['node_id'] = convert_nodeid(list_data['node_id'])
      if ((data['id']['get_time_no'] - tmp_startdt).seconds  < 60):
        tmp_enddt   = data['id']['get_time_no']
        del(data['_id'])

        if (data["nodelist"][0]["node_id"] != tmp_node_id):
          se_data =  {"mac":data["id"]["mac"],
                      "start_time":tmp_startdt,
                      "end_time"  :tmp_enddt,
                      "interval"  :(tmp_enddt - tmp_startdt).seconds,
                      "start_node":tmp_node_id,
                      "end_node"  :data["nodelist"][0]["node_id"],
                      }
          data_lists.append(se_data)

          if se_data["mac"] in mac_list_experiment:
            data_lists_experiment.append(se_data)
          count += 1
          
      tmp_node_id = data["nodelist"][0]["node_id"]
      tmp_startdt = data['id']['get_time_no']

    else:
      tmp_mac = data["id"]["mac"]
      data['id']['get_time_no'] = datetime.strptime(str(data['id']['get_time_no']), '%Y%m%d%H%M%S')
      tmp_startdt = data['id']['get_time_no']

    count_all += 1

  data_lists = sorted(data_lists, key=lambda x:x["start_time"], reverse=True)
  data_lists_experiment = sorted(data_lists_experiment, key=lambda x:x["start_time"], reverse=True)

  import time
  start = time.time()
  make_pfvinfo(data_lists)
  end = time.time()
  print("time:"+str(end-start))
  # make_pfvinfo_experiment(data_lists_experiment)

  return render_to_response('pfv/get_start_end.html',  # 使用するテンプレート
                              {"datas":data_lists, "count":count, "count_all":count_all} 
                            )  