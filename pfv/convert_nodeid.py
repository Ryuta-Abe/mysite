# -*- coding: utf-8 -*-

W2_6F_node = [1236,1237,1238,1239,1240,1241,1242,     1244,1245,
           1246,1247,1248,1249,1250,1251,1252,1253,1254,1255,
           1256,1257,1258,1259,1260,     1386]
W2_7F_node = [1262,1263,1264,1265,1266,1267,1268,1269,1270,1271,
           1272,1273,1274,1275,1276,1277,1278,1279,1280,
           1282,1283,1284,1285,1286,     1298,1299]


def convert_nodeid(n_id):
  if (n_id in W2_6F_node):
    floor = "W2-6F"
    if (n_id == 1236):
      n_id = 27
    elif(n_id == 1237):
      n_id = 2
    elif(n_id == 1238):
      n_id = 3
    elif(n_id == 1239):
      n_id = 1
    elif(n_id == 1240):
      n_id = 4
    elif(n_id == 1241):
      n_id = 5
    elif(n_id == 1242):
      n_id = 6
    elif(n_id == 1244):
      n_id = 8
    elif(n_id == 1245):
      n_id = 9
    elif(n_id == 1246):
      n_id = 10
    elif(n_id == 1247):
      n_id = 11
    elif(n_id == 1248):
      n_id = 12
    elif(n_id == 1249):
      n_id = 13
    elif(n_id == 1250):
      n_id = 14
    elif(n_id == 1251):
      n_id = 15
    elif(n_id == 1252):
      n_id = 16
    elif(n_id == 1253):
      n_id = 17
    elif(n_id == 1254):
      n_id = 18
    elif(n_id == 1255):
      n_id = 19
    elif(n_id == 1256):
      n_id = 20
    elif(n_id == 1257):
      n_id = 21
    elif(n_id == 1258):
      n_id = 22
    elif(n_id == 1259):
      n_id = 23
    elif(n_id == 1260):
      n_id = 24
    elif(n_id == 1386):
      n_id = 7
    else:
      n_id = 9999

  elif (n_id in W2_7F_node):
    floor = "W2-7F"
    if (n_id == 1262):
      n_id = 25
    elif(n_id == 1263):
      n_id = 1
    elif(n_id == 1264):
      n_id = 2
    elif(n_id == 1265):
      n_id = 3
    elif(n_id == 1266):
      n_id = 4
    elif(n_id == 1267):
      n_id = 5
    elif(n_id == 1268):
      n_id = 6
    elif(n_id == 1269):
      n_id = 7
    elif(n_id == 1270):
      n_id = 8
    elif(n_id == 1271):
      n_id = 9
    elif(n_id == 1272):
      n_id = 10
    elif(n_id == 1273):
      n_id = 11
    elif(n_id == 1274):
      n_id = 12
    elif(n_id == 1275):
      n_id = 13
    elif(n_id == 1276):
      n_id = 14
    elif(n_id == 1277):
      n_id = 15
    elif(n_id == 1278):
      n_id = 16
    elif(n_id == 1279):
      n_id = 17
    elif(n_id == 1280):
      n_id = 18
    elif(n_id == 1282):
      n_id = 20
    elif(n_id == 1283):
      n_id = 21
    elif(n_id == 1284):
      n_id = 22
    elif(n_id == 1285):
      n_id = 23
    elif(n_id == 1286):
      n_id = 24
    elif(n_id == 1298):
      n_id = 26
    elif(n_id == 1299):
      n_id = 27
    else:
      n_id = 9999

  return n_id