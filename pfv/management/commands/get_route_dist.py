# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from pfv.models import pcwlroute
from pfv.get_start_end import get_min_distance

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