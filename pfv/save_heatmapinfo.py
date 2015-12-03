import datetime
import math

#mongoDBに接続
from mongoengine import *
from pymongo import *

# from pfv.models import pcwlnode, pfvinfo, pfvmacinfo, pfvinfoexperiment, pfvinfoexperiment2, pcwlroute, pcwltime, stayinfo, staymacinfo, heatmapinfo

client = MongoClient()
db = client.nm4bd
db.pcwltime.create_index([("datetime", ASCENDING)])
db.pfvinfo.create_index([("datetime", ASCENDING)])
db.stayinfo.create_index([("datetime", ASCENDING)])
db.pcwlroute.create_index([("query", ASCENDING)])

# heatmapinfoのモデル
class heatmapinfo(Document):
    datetime = DateTimeField()
    coordinate_size = ListField(DictField())
    floor = StringField()

    meta = {
        "db_alias" : "nm4bd",
    }

#座標の作成
coordinate_width = 50
coordinate = []
hor = 0
ver = 0
while hor * coordinate_width < 1024:
    while ver * coordinate_width < 560:
        x = hor * coordinate_width
        y = ver * coordinate_width
        coordinate.append({"pos_x":x, "pos_y":y})
        ver += 1
    hor += 1
    ver = 0

# pcwl情報の取り出し
pcwlnode = []
pcwlnode += db.pcwlnode.find()

#plist内のdirectionと座標を紐付け
def direction_to_coordinate(direction):
    coordinate_info = []
    point_list = []
    for i in pcwlnode:
        if i["pcwl_id"] == direction[0]:
            c1 = i
        if i["pcwl_id"] == direction[1]:
            c2 = i
    point_list.append({"pos_x":c1["pos_x"], "pos_y":c1["pos_y"]})
    point_list.append({"pos_x":c2["pos_x"], "pos_y":c2["pos_y"]})
    center_x = (c1["pos_x"] + c2["pos_x"]) / 2
    center_y = (c1["pos_y"] + c2["pos_y"]) / 2
    point_list.append({"pos_x":center_x, "pos_y":center_y})
    center_x_1 = (c1["pos_x"] + center_x) / 2
    center_y_1 = (c1["pos_y"] + center_y) / 2
    point_list.append({"pos_x":center_x_1, "pos_y":center_y_1})
    center_x_2 = (c2["pos_x"] + center_x) / 2
    center_y_2 = (c2["pos_y"] + center_y) / 2
    point_list.append({"pos_x":center_x_2, "pos_y":center_y_2})
    hor = 0
    ver = 0
    while hor * coordinate_width < 1024:
        while ver * coordinate_width < 560:
            x1 = hor * coordinate_width
            y1 = ver * coordinate_width
            x2 = (hor + 1) * coordinate_width
            y2 = (ver + 1) * coordinate_width
            for i in point_list:
                if x1 <= i["pos_x"] and i["pos_x"] <= x2 and y1 <= i["pos_y"] and i["pos_y"] <= y2:
                    coordinate_info.append({"pos_x":x1, "pos_y":y1})
                    break
            ver += 1
        hor += 1
        ver = 0
    return coordinate_info

# #heatmap用のデータをheatmapinfoに保存
# def save_heatmapinfo(coordinate_info):
#     # 開始時にDBを初期化
#     db.heatmapinfo.remove()

#     pfvinfo = []
#     pfvinfo += db.pfvinfo.find()
#     for i in pfvinfo:
#         size_list = []
#         for plist in i["plist"]:
#             tmp_info = direction_to_coordinate(plist["direction"])
#             for k in tmp_info:
#                 size_list.append({"pos_x":k["pos_x"],"pos_y":k["pos_y"],"size":plist["size"]})
#         _heatmapinfo = heatmapinfo(
#                         datetime = i["datetime"],
#                         coordinate_size = size_list,
#                         # floor = i["floor"],
#                                     )
#         _heatmapinfo.save()
    # return render_to_response('pfv/pfv_heatmap.html')

#heatmap用のデータをheatmapinfoに保存
def save_heatmapinfo(coordinate_info):
    # 開始時にDBを初期化
    db.heatmapinfo.remove()

    pfvinfo = []
    pfvinfo += db.pfvinfo.find()

    hor = 0 #横
    ver = 0 #縦
    for i in pfvinfo:
        size_list = []
        while hor * coordinate_width < 1024:
            while ver * coordinate_width < 560:
                size_count = 0
                x = hor * coordinate_width
                y = ver * coordinate_width
                for plist in i["plist"]:
                    if plist["size"] != 0:
                        tmp_info = direction_to_coordinate(plist["direction"])
                        for k in tmp_info:
                            if k["pos_x"] == x and k["pos_y"] == y:
                                size_count += plist["size"]
                size_list.append({"pos_x":x,"pos_y":y,"size":size_count})
                ver += 1
            hor += 1
            ver = 0
        hor = 0
        _heatmapinfo = heatmapinfo(
                        datetime = i["datetime"],
                        coordinate_size = size_list,
                        floor = i["floor"],
                                    )
        _heatmapinfo.save()

#save手順
#save_heatmapinfoをurlsのimportに追加
#urlsのpfv_heatmapをコメントアウトし、以下を追加
#url(r'^pfv_heatmap/$', save_heatmapinfo.save_heatmapinfo, name='save_heatmapinfo'), #save用
#以下のurlで実行
#http://localhost:8000/pfv/pfv_heatmap/