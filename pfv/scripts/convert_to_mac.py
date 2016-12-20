# -*- coding: utf-8 -*-
# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd
import sys

def make_tag_id_collection():
    db.tag_id.insert({"tag_id":6,"mac":"00:11:81:10:01:1c"})
    # db.tag_id.insert({"tag_id":7,"mac":"00:11:81:10:01:18"})
    db.tag_id.insert({"tag_id":8,"mac":"00:11:81:10:01:19"})
    db.tag_id.insert({"tag_id":9,"mac":"00:11:81:10:01:17"})
    # db.tag_id.insert({"tag_id":10,"mac":"00:11:81:10:01:16"})
    db.tag_id.insert({"tag_id":11,"mac":"00:11:81:10:01:1a"})
    # db.tag_id.insert({"tag_id":12,"mac":"00:11:81:10:01:23"})
    db.tag_id.insert({"tag_id":13,"mac":"00:11:81:10:01:1b"})
    db.tag_id.insert({"tag_id":14,"mac":"00:11:81:10:01:1e"})
    db.tag_id.insert({"tag_id":15,"mac":"00:11:81:10:01:1d"})
    db.tag_id.insert({"tag_id":16,"mac":"00:11:81:10:01:11"})
    db.tag_id.insert({"tag_id":17,"mac":"00:11:81:10:01:22"})
    db.tag_id.insert({"tag_id":19,"mac":"00:11:81:10:01:20"})
    db.tag_id.insert({"tag_id":20,"mac":"00:11:81:10:01:21"})
    db.tag_id.insert({"tag_id":21,"mac":"00:11:81:10:01:00"})
    db.tag_id.insert({"tag_id":22,"mac":"00:11:81:10:01:01"})
    db.tag_id.insert({"tag_id":23,"mac":"00:11:81:10:01:02"})
    db.tag_id.insert({"tag_id":24,"mac":"00:11:81:10:01:03"})
    db.tag_id.insert({"tag_id":25,"mac":"00:11:81:10:01:52"})
    db.tag_id.insert({"tag_id":26,"mac":"00:11:81:10:01:04"})
    db.tag_id.insert({"tag_id":27,"mac":"00:11:81:10:01:05"})
    db.tag_id.insert({"tag_id":28,"mac":"00:11:81:10:01:06"})
    db.tag_id.insert({"tag_id":29,"mac":"00:11:81:10:01:07"})
    db.tag_id.insert({"tag_id":30,"mac":"00:11:81:10:01:08"})
    db.tag_id.insert({"tag_id":31,"mac":"00:11:81:10:01:0a"})
    db.tag_id.insert({"tag_id":32,"mac":"00:11:81:10:01:0b"})
    db.tag_id.insert({"tag_id":33,"mac":"00:11:81:10:01:0d"})
    db.tag_id.insert({"tag_id":35,"mac":"00:11:81:10:01:0c"})
    db.tag_id.insert({"tag_id":36,"mac":"00:11:81:10:01:24"})
    db.tag_id.insert({"tag_id":37,"mac":"00:11:81:10:01:25"})
    db.tag_id.insert({"tag_id":38,"mac":"00:11:81:10:01:26"})
    db.tag_id.insert({"tag_id":39,"mac":"00:11:81:10:01:0e"})
    db.tag_id.insert({"tag_id":40,"mac":"00:11:81:10:01:0f"})
    db.tag_id.insert({"tag_id":41,"mac":"00:11:81:10:01:3d"})
    db.tag_id.insert({"tag_id":42,"mac":"00:11:81:10:01:3f"})
    db.tag_id.insert({"tag_id":43,"mac":"00:11:81:10:01:3e"})
    db.tag_id.insert({"tag_id":44,"mac":"00:11:81:10:01:40"})
    db.tag_id.insert({"tag_id":45,"mac":"00:11:81:10:01:41"})
    db.tag_id.insert({"tag_id":46,"mac":"00:11:81:10:01:43"})
    db.tag_id.insert({"tag_id":47,"mac":"00:11:81:10:01:44"})
    db.tag_id.insert({"tag_id":48,"mac":"00:11:81:10:01:45"})
    db.tag_id.insert({"tag_id":49,"mac":"00:11:81:10:01:46"})
    db.tag_id.insert({"tag_id":50,"mac":"00:11:81:10:01:42"})
    db.tag_id.insert({"tag_id":51,"mac":"00:11:81:10:01:4a"})
    db.tag_id.insert({"tag_id":52,"mac":"00:11:81:10:01:4c"})
    db.tag_id.insert({"tag_id":53,"mac":"00:11:81:10:01:48"})
    db.tag_id.insert({"tag_id":54,"mac":"00:11:81:10:01:49"})
    db.tag_id.insert({"tag_id":55,"mac":"00:11:81:10:01:47"})
    db.tag_id.insert({"tag_id":61,"mac":"00:11:81:10:01:28"})
    db.tag_id.insert({"tag_id":62,"mac":"00:11:81:10:01:29"})
    db.tag_id.insert({"tag_id":63,"mac":"00:11:81:10:01:2b"})
    db.tag_id.insert({"tag_id":64,"mac":"00:11:81:10:01:2c"})
    db.tag_id.insert({"tag_id":65,"mac":"00:11:81:10:01:2d"})
    db.tag_id.insert({"tag_id":66,"mac":"00:11:81:10:01:2e"})

def convert_to_mac(tag_id):
	if isinstance(tag_id,str):
		tag_id = int(tag_id)
	elif isinstance(tag_id,int):
		pass
	else:
		print("argument's type error!")

	tag_info = db.tag_id.find_one({"tag_id":tag_id})
	return tag_info["mac"]

if __name__ == '__main__':
	param = sys.argv
	if len(param) == 1:
		make_tag_id_collection()
	elif len(param) == 2:
		print(convert_to_mac(param[1]))
	else:
		print("argument's num. error!")






