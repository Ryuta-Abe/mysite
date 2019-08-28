import sys,os, csv
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
from pymongo import *
import config
client = MongoClient()
db = client.nm4bd

# def get_pcwl_index(floor,pcwl_id,inputs_list = False):
def get_pcwl_index(floor,pcwl_id):
    if type(pcwl_id) is int:
        inputs_list = False
    else:
        inputs_list = True
    pcwl_id_list = []
    floor_node_col = db.reg_pcwlnode.find({"floor":floor}).sort("pcwl_id",ASCENDING)
    for node in floor_node_col:
        pcwl_id_list.append(node["pcwl_id"])
    if inputs_list:
        index_list = []
        for one_pcwl_id in pcwl_id:
            index = pcwl_id_list.index(one_pcwl_id)
            index_list.append(index)
        return index_list
    else:
        index = pcwl_id_list.index(pcwl_id)
        return index

def get_m_from_px(px_distance, digit_to_round = 2):
    distance =  px_distance * 14.4 / 110
    distance = round(distance, digit_to_round)
    return distance

def get_list_from_csv(csv_file):
    with open(csv_file) as f:
        reader = csv.reader(f, delimiter=",")
        result_list = [row for row in reader]
    return result_list

if __name__ == "__main__":
    index = get_pcwl_index("W2-7F",5)
    print(index)
    index_list = get_pcwl_index("W2-7F",[2,4,6,10,14,15,17,20,23,24,25,26,27])
    print(index_list)
