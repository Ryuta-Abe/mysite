# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from pfv.models import pr_req, test, pcwltime
from mongoengine import *
from pymongo import *

import json
import math
import datetime
import locale

def make_pcwltime(self):
    ag = test._get_collection().aggregate([
                                          {"$group":
                                            {"_id":
                                              {"get_time_no":"$get_time_no",}
                                            },
                                          },
                                          {"$out": "tmppcwltime"},
                                        ],
                                      allowDiskUse=True,
                                      )
    jdatas = db.tmppcwltime.find()
    pcwltime.objects.all().delete()

    for jdata in jdatas:
    	jdata['datetime'] = datetime.strptime(str(jdata['_id']['get_time_no']), '%Y%m%d%H%M%S')
    	del(jdata['_id'])
    	timedata = pcwltime(
    		datetime = jdata['datetime'],
    		)
    	timedata.save()