# -*- coding: utf-8 -*-
from pymongo import *
client = MongoClient()
db = client.nm4bd

class Position():
    position = []

    def __init__(self,prev_node,prev_distance,next_distance,next_node):
        self.position = [prev_node,prev_distance,next_distance,next_node]


class PCWL():
    mac = ""
    pos_x = 0
    pos_y = 0
    position = Position()
    ip = ""
    floor = ""
    pcwl_id = 0
    def __init__(self,floor,pcwl_id):
        self.floor = floor
        self.pcwl_id = pcwl_id
    
    def __init__(self,ip):
        self.ip = ip
        ip_dict = db.pcwliplist.find_one({"ip":self.ip}) #pick up what is needed 
        self.floor = ip_dict["floor"]
        self.pcwl_id = ip_dict["pcwl_id"]

if __name__ == "__main__":
    pcwl = PCWL("10.0.11.47")
    print(pcwl.floor)

