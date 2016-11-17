# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../scripts')
from pfv.models import pcwlroute
from get_start_end import *

from pymongo import *

client = MongoClient()
db = client.nm4bd

class Command(BaseCommand):
  # args = '<target_id target_id ...>'
  help = u'st_node,ed_node -> route distance'

  def handle(self, *args, **options):
    floor = str(args[0])
    st_node, ed_node = int(args[1]), int(args[2])
    total_dist = get_min_distance(floor, st_node, ed_node)

    print(floor, st_node, ed_node)
    print("dist:"+str(total_dist))