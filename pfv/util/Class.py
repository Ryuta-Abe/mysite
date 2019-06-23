# -*- coding: utf-8 -*-
from pymongo import *
client = MongoClient()
db = client.nm4bd
class Position():
    def __init__(self,position_list,floor = "None"):
        self.pos_x = 0
        self.pos_y = 0
        self.position = position_list
        self.prev_node = position_list[0]
        self.prev_dist = position_list[1]
        self.next_dist = position_list[2]
        self.next_node = position_list[3]
        self.floor = floor
    
    def get_pos_xy(self):
        self.pos_x, self.pos_y = get_position(self.floor,self.position)
        return self.pos_x, self.pos_y

    def update_position(self):
        self.position = [self.prev_node,self.prev_dist,self.next_dist,self.next_node]

    def reverse_order(self):
        self.prev_node, self.next_node = self.next_node, self.prev_node
        self.prev_dist, self.next_dist = self.next_dist, self.prev_dist
        self.update_position()
        return self.position

    def is_intersection(self):
        if(self.prev_dist == 0):
            node_info = db.pcwlnode.find_one({"floor":self.floor,"pcwl_id":self.prev_node})
            # Note: Type Error時はinit時にfloorが与えられておらず、初期値のNoneが入っている
            if len(node_info["next_id"]) >= 3:
                return True
        if(self.next_dist == 0):
            node_info = db.pcwlnode.find_one({"floor":self.floor,"pcwl_id":self.next_node})
            if len(node_info["next_id"]) >= 3:
                return True
        return False
                
class Node():
    mac = ""
    pos_x = 0
    pos_y = 0
    position = Position([0,0,0,0])
    ip = ""
    floor = ""
    pcwl_id = 0
    def __init__(self,*input):
        if(len(input) == 2):
            self.floor = input[0]
            self.pcwl_id = input[1]
            self.position = Position(self.get_position())
        if(len(input) == 1):
            self.ip = input[0]
            ip_dict = db.pcwliplist.find_one({"ip":self.ip}) #pick up what is needed 
            self.floor = ip_dict["floor"]
            self.pcwl_id = ip_dict["pcwl_id"]

    def get_position(self):
        pcwl_info = db.pcwlnode.find_one({"floor":self.floor,"pcwl_id":self.pcwl_id})
        next_id = pcwl_info["next_id"][0]
        next_dist = db.idealroute.find_one({"$and": [{"floor" : self.floor},
										{"query" : self.pcwl_id}, {"query" : next_id}]})["total_distance"]
        position = [self.pcwl_id, 0 , next_dist, next_id]
        return position
    
    def is_intersection(self):
        pcwl_info = db.pcwlnode.find_one({"floor":self.floor,"pcwl_id":self.pcwl_id})
        if (len(pcwl_info["next_id"]) >= 3):
            return True
        else:
            return False

# class Nodelist():
#     floor = ""
#     rssi = ""
#     position = Position([0,0,0,0])
#     nodelist = [floor,position.position,rssi]
def get_position(floor,position_list):
	prev_node,prev_distance,next_distance,next_node = position_list
	prev_node = db.pcwlnode.find_one({"floor" : floor,"pcwl_id":prev_node})
	prev_pos_x = prev_node["pos_x"]
	prev_pos_y = prev_node["pos_y"]
	next_node = db.pcwlnode.find_one({"floor" : floor,"pcwl_id":next_node})
	next_pos_x = next_node["pos_x"]
	next_pos_y = next_node["pos_y"]
	delta_x = abs(prev_pos_x - next_pos_x)
	if delta_x == 0:
		pos_x = prev_pos_x
	else:
		pos_x = (prev_pos_x * next_distance + next_pos_x * prev_distance) / (prev_distance + next_distance)
	delta_y = abs(prev_pos_y - next_pos_y)
	if delta_y == 0:
		pos_y = prev_pos_y
	else:
		pos_y = (prev_pos_y * next_distance + next_pos_y * prev_distance) / (prev_distance + next_distance)
	return pos_x, pos_y


if __name__ == "__main__":
    # pos = Position([1,2,5,3])
    # pos.reverse_order()
    # print(pos.position)
    # pos.get_pos_xy()
    # print(pos.pos_x,pos.pos_y)

    pos = Node("W2-7F",25)
    result = pos.get_position()
    print(result)