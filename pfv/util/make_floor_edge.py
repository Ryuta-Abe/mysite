# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import sys, os
from pymongo import *

client = MongoClient()
db = client.nm4bd
db.floor_edge.drop()

FLOOR_LIST = ["W2-6F","W2-7F","W2-8F","W2-9F"]

def make_floor_edge(floor):
	"""
	フロア内の辺(両端の座標)を保存したコレクション(floor_edge)を作成する
	@param  floor:str
	"""
	nodes = db.pcwlnode.find({"floor":floor})
	edge_list = []
	for node in nodes:
		for n_node in node["next_id"]:
			n_node_info = db.pcwlnode.find_one({"floor":floor, "pcwl_id":n_node})
			tmp_edge = [node["pcwl_id"], n_node_info["pcwl_id"]]
			rev_edge = [n_node_info["pcwl_id"], node["pcwl_id"]]

			node1 = {"pcwl_id":node["pcwl_id"], "pos_x":node["pos_x"], "pos_y":node["pos_y"]}
			node2 = {"pcwl_id":n_node_info["pcwl_id"], "pos_x":n_node_info["pos_x"], "pos_y":n_node_info["pos_y"]}
			# print(tmp_edge)
			if edge_list == []:
				ins_data = [node1,node2]
				db.floor_edge.insert({"floor":floor, "edge":ins_data})
				edge_list.append(tmp_edge)

			ins_flag = True
			for edge in edge_list:
				if (tmp_edge == edge or rev_edge == edge):
					ins_flag = False
					break

			if ins_flag:
				ins_data = [node1,node2]
				db.floor_edge.insert({"floor":floor, "edge":ins_data})
				edge_list.append(tmp_edge)
				print(tmp_edge)


if __name__ == '__main__':
	for floor in FLOOR_LIST:
		make_floor_edge(floor)





