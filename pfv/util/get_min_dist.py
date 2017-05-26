# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import sys, os
from pymongo import *

client = MongoClient()
db = client.nm4bd

# rounding in specified place
def rounding(num, round_place):
	rounded_num = round(num*pow(10, round_place)) / pow(10, round_place)
	return rounded_num

def func(floor, st_node, ed_node):
	query = {"$and" : [{"floor":floor},{"query":st_node},{"query":ed_node}]}
	route_data = db.idealroute.find_one(query)
	if route_data != None:
		print(route_data["floor"]+" , "+str(st_node)+"->"+str(ed_node)+" , "+ str(rounding(route_data["total_distance"],1)))
	else:
		print("=== None data of "+str(st_node)+"->"+str(ed_node))

"""
指定フロア・AP間の最短距離算出
"""
if __name__ == '__main__':
	r_list = []
	floor = "W2-7F"
	func(floor,5,3)





