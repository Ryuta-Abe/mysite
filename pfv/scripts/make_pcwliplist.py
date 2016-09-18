# -*- coding: utf-8 -*-
# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

db.pcwliplist.remove() # 一旦DBを空に

# W2-6F
db.pcwliplist.insert({"ip":"10.0.11.5" ,"node_id":1239,"floor":"W2-6F","pcwl_id":1}) # 1
db.pcwliplist.insert({"ip":"10.0.11.27","node_id":1237,"floor":"W2-6F","pcwl_id":2}) # 2
db.pcwliplist.insert({"ip":"10.0.11.37","node_id":1238,"floor":"W2-6F","pcwl_id":3}) # 3
db.pcwliplist.insert({"ip":"10.0.12.71","node_id":1240,"floor":"W2-6F","pcwl_id":4}) # 4
db.pcwliplist.insert({"ip":"10.0.12.79","node_id":1241,"floor":"W2-6F","pcwl_id":5}) # 5
db.pcwliplist.insert({"ip":"10.0.12.81","node_id":1242,"floor":"W2-6F","pcwl_id":6}) # 6
db.pcwliplist.insert({"ip":"10.0.12.29","node_id":1386,"floor":"W2-6F","pcwl_id":7}) # 7
db.pcwliplist.insert({"ip":"10.0.11.21","node_id":1244,"floor":"W2-6F","pcwl_id":8}) # 8
db.pcwliplist.insert({"ip":"10.0.11.39","node_id":1245,"floor":"W2-6F","pcwl_id":9}) # 9
db.pcwliplist.insert({"ip":"10.0.11.33","node_id":1246,"floor":"W2-6F","pcwl_id":10}) # 10
db.pcwliplist.insert({"ip":"10.0.11.31","node_id":1247,"floor":"W2-6F","pcwl_id":11}) # 11
db.pcwliplist.insert({"ip":"10.0.11.35","node_id":1248,"floor":"W2-6F","pcwl_id":12}) # 12
db.pcwliplist.insert({"ip":"10.0.11.9" ,"node_id":1249,"floor":"W2-6F","pcwl_id":13}) # 13
db.pcwliplist.insert({"ip":"10.0.11.15","node_id":1250,"floor":"W2-6F","pcwl_id":14}) # 14
db.pcwliplist.insert({"ip":"10.0.11.17","node_id":1251,"floor":"W2-6F","pcwl_id":15}) # 15
db.pcwliplist.insert({"ip":"10.0.11.13","node_id":1252,"floor":"W2-6F","pcwl_id":16}) # 16
db.pcwliplist.insert({"ip":"10.0.11.19","node_id":1253,"floor":"W2-6F","pcwl_id":17}) # 17
db.pcwliplist.insert({"ip":"10.0.11.11","node_id":1254,"floor":"W2-6F","pcwl_id":18}) # 18
db.pcwliplist.insert({"ip":"10.0.11.29","node_id":1255,"floor":"W2-6F","pcwl_id":19}) # 19
db.pcwliplist.insert({"ip":"10.0.11.7" ,"node_id":1256,"floor":"W2-6F","pcwl_id":20}) # 20
db.pcwliplist.insert({"ip":"10.0.12.69","node_id":1257,"floor":"W2-6F","pcwl_id":21}) # 21
db.pcwliplist.insert({"ip":"10.0.12.77","node_id":1258,"floor":"W2-6F","pcwl_id":22}) # 22
db.pcwliplist.insert({"ip":"10.0.12.67","node_id":1259,"floor":"W2-6F","pcwl_id":23}) # 23
db.pcwliplist.insert({"ip":"10.0.12.75","node_id":1260,"floor":"W2-6F","pcwl_id":24}) # 24
# db.pcwliplist.insert({"ip":"10.0.1.25","node_id":25}) # 25
# db.pcwliplist.insert({"ip":"10.0.1.25","node_id":26}) # 26
db.pcwliplist.insert({"ip":"10.0.11.25","node_id":1236,"floor":"W2-6F","pcwl_id":27}) # 27

# W2-7F
db.pcwliplist.insert({"ip":"10.0.11.147","node_id":1263,"floor":"W2-7F","pcwl_id":1}) # 1
db.pcwliplist.insert({"ip":"10.0.11.141","node_id":1264,"floor":"W2-7F","pcwl_id":2}) # 2
db.pcwliplist.insert({"ip":"10.0.11.149","node_id":1265,"floor":"W2-7F","pcwl_id":3}) # 3
db.pcwliplist.insert({"ip":"10.0.11.157","node_id":1266,"floor":"W2-7F","pcwl_id":4}) # 4
db.pcwliplist.insert({"ip":"10.0.11.59" ,"node_id":1267,"floor":"W2-7F","pcwl_id":5}) # 5
db.pcwliplist.insert({"ip":"10.0.11.51" ,"node_id":1268,"floor":"W2-7F","pcwl_id":6}) # 6
db.pcwliplist.insert({"ip":"10.0.11.45" ,"node_id":1269,"floor":"W2-7F","pcwl_id":7}) # 7
db.pcwliplist.insert({"ip":"10.0.11.43" ,"node_id":1270,"floor":"W2-7F","pcwl_id":8}) # 8
db.pcwliplist.insert({"ip":"10.0.11.41" ,"node_id":1271,"floor":"W2-7F","pcwl_id":9}) # 9
db.pcwliplist.insert({"ip":"10.0.11.49" ,"node_id":1272,"floor":"W2-7F","pcwl_id":10}) # 10
db.pcwliplist.insert({"ip":"10.0.11.47" ,"node_id":1273,"floor":"W2-7F","pcwl_id":11}) # 11
db.pcwliplist.insert({"ip":"10.0.11.153","node_id":1274,"floor":"W2-7F","pcwl_id":12}) # 12
db.pcwliplist.insert({"ip":"10.0.11.151","node_id":1275,"floor":"W2-7F","pcwl_id":13}) # 13
db.pcwliplist.insert({"ip":"10.0.11.159","node_id":1276,"floor":"W2-7F","pcwl_id":14}) # 14
db.pcwliplist.insert({"ip":"10.0.12.33" ,"node_id":1277,"floor":"W2-7F","pcwl_id":15}) # 15
db.pcwliplist.insert({"ip":"10.0.12.27" ,"node_id":1278,"floor":"W2-7F","pcwl_id":16}) # 16
db.pcwliplist.insert({"ip":"10.0.12.43" ,"node_id":1279,"floor":"W2-7F","pcwl_id":17}) # 17
db.pcwliplist.insert({"ip":"10.0.12.39" ,"node_id":1280,"floor":"W2-7F","pcwl_id":18}) # 18
# db.pcwliplist.insert({"ip":"10.0.1.25","node_id":19}) # 19
db.pcwliplist.insert({"ip":"10.0.11.57" ,"node_id":1282,"floor":"W2-7F","pcwl_id":20}) # 20
db.pcwliplist.insert({"ip":"10.0.12.31" ,"node_id":1283,"floor":"W2-7F","pcwl_id":21}) # 21
db.pcwliplist.insert({"ip":"10.0.12.25" ,"node_id":1284,"floor":"W2-7F","pcwl_id":22}) # 22
db.pcwliplist.insert({"ip":"10.0.12.41" ,"node_id":1285,"floor":"W2-7F","pcwl_id":23}) # 23
db.pcwliplist.insert({"ip":"10.0.11.155","node_id":1286,"floor":"W2-7F","pcwl_id":24}) # 24
db.pcwliplist.insert({"ip":"10.0.11.145","node_id":1262,"floor":"W2-7F","pcwl_id":25}) # 25
db.pcwliplist.insert({"ip":"10.0.12.47" ,"node_id":1298,"floor":"W2-7F","pcwl_id":26}) # 26
db.pcwliplist.insert({"ip":"10.0.12.37" ,"node_id":1299,"floor":"W2-7F","pcwl_id":27}) # 27

# W2-8F
db.pcwliplist.insert({"ip":"10.0.2.88","node_id":1315,"floor":"W2-8F","pcwl_id":1 }) # 1
db.pcwliplist.insert({"ip":"10.0.8.92","node_id":1316,"floor":"W2-8F","pcwl_id":2 }) # 2
db.pcwliplist.insert({"ip":"10.0.7.82","node_id":1317,"floor":"W2-8F","pcwl_id":3 }) # 3
db.pcwliplist.insert({"ip":"10.0.2.82","node_id":1318,"floor":"W2-8F","pcwl_id":4 }) # 4
db.pcwliplist.insert({"ip":"10.0.2.254","node_id":1319,"floor":"W2-8F","pcwl_id":5 }) # 5
db.pcwliplist.insert({"ip":"10.0.0.166","node_id":1320,"floor":"W2-8F","pcwl_id":6 }) # 6
db.pcwliplist.insert({"ip":"10.0.5.10","node_id":1321,"floor":"W2-8F","pcwl_id":7 }) # 7
db.pcwliplist.insert({"ip":"10.0.2.164","node_id":1322,"floor":"W2-8F","pcwl_id":8 }) # 8
# db.pcwliplist.insert({"ip":"10.0.3.6","node_id":1323,"floor":"W2-8F","pcwl_id":9 }) # 9
db.pcwliplist.insert({"ip":"10.0.0.180","node_id":1324,"floor":"W2-8F","pcwl_id":10}) # 10
db.pcwliplist.insert({"ip":"10.0.8.74","node_id":1344,"floor":"W2-8F","pcwl_id":11}) # 11
db.pcwliplist.insert({"ip":"10.0.2.154","node_id":1326,"floor":"W2-8F","pcwl_id":12}) # 12
db.pcwliplist.insert({"ip":"10.0.8.82","node_id":1327,"floor":"W2-8F","pcwl_id":13}) # 13
db.pcwliplist.insert({"ip":"10.0.2.80","node_id":1328,"floor":"W2-8F","pcwl_id":14}) # 14
db.pcwliplist.insert({"ip":"10.0.0.168","node_id":1329,"floor":"W2-8F","pcwl_id":15}) # 15
db.pcwliplist.insert({"ip":"10.0.7.72","node_id":1330,"floor":"W2-8F","pcwl_id":16}) # 16
db.pcwliplist.insert({"ip":"10.0.0.136","node_id":1331,"floor":"W2-8F","pcwl_id":17}) # 17
db.pcwliplist.insert({"ip":"10.0.7.70","node_id":1332,"floor":"W2-8F","pcwl_id":18}) # 18
db.pcwliplist.insert({"ip":"10.0.0.130","node_id":1333,"floor":"W2-8F","pcwl_id":19}) # 19
# db.pcwliplist.insert({"ip":"10.0.2.250","node_id":1334,"floor":"W2-8F","pcwl_id":20}) # 20
# db.pcwliplist.insert({"ip":"10.0.8.90","node_id":1335,"floor":"W2-8F","pcwl_id":21}) # 21
# db.pcwliplist.insert({"ip":"10.0.3.2","node_id":1336,"floor":"W2-8F","pcwl_id":22}) # 22
# db.pcwliplist.insert({"ip":"10.0.3.0","node_id":1337,"floor":"W2-8F","pcwl_id":23}) # 23
# db.pcwliplist.insert({"ip":"10.0.2.128","node_id":1338,"floor":"W2-8F","pcwl_id":24}) # 24
# db.pcwliplist.insert({"ip":"10.0.0.128","node_id":1346,"floor":"W2-8F","pcwl_id":25}) # 25
# db.pcwliplist.insert({"ip":"10.0.2.74","node_id":1340,"floor":"W2-8F","pcwl_id":26}) # 26
# db.pcwliplist.insert({"ip":"10.0.5.20","node_id":1341,"floor":"W2-8F","pcwl_id":27}) # 27
# db.pcwliplist.insert({"ip":"10.0.2.86","node_id":1314,"floor":"W2-8F","pcwl_id":28}) # 28
# db.pcwliplist.insert({"ip":"10.0.0.176","node_id":1342,"floor":"W2-8F","pcwl_id":29}) # 29
# db.pcwliplist.insert({"ip":"10.0.2.116","node_id":1343,"floor":"W2-8F","pcwl_id":30}) # 30

# W2-9F
db.pcwliplist.insert({"ip":"10.0.11.69","node_id":1288,"floor":"W2-9F","pcwl_id":1 }) # 1
db.pcwliplist.insert({"ip":"10.0.11.67","node_id":1289,"floor":"W2-9F","pcwl_id":2 }) # 2
db.pcwliplist.insert({"ip":"10.0.11.65","node_id":1290,"floor":"W2-9F","pcwl_id":3 }) # 3
db.pcwliplist.insert({"ip":"10.0.11.61","node_id":1291,"floor":"W2-9F","pcwl_id":4 }) # 4
db.pcwliplist.insert({"ip":"10.0.11.53","node_id":1292,"floor":"W2-9F","pcwl_id":5 }) # 5
db.pcwliplist.insert({"ip":"10.0.11.79","node_id":1293,"floor":"W2-9F","pcwl_id":6 }) # 6
db.pcwliplist.insert({"ip":"10.0.11.75","node_id":1294,"floor":"W2-9F","pcwl_id":7 }) # 7
db.pcwliplist.insert({"ip":"10.0.11.71","node_id":1295,"floor":"W2-9F","pcwl_id":8 }) # 8
db.pcwliplist.insert({"ip":"10.0.11.63","node_id":1296,"floor":"W2-9F","pcwl_id":9 }) # 9
db.pcwliplist.insert({"ip":"10.0.11.55","node_id":1297,"floor":"W2-9F","pcwl_id":10}) # 10
db.pcwliplist.insert({"ip":"10.0.11.119","node_id":1300,"floor":"W2-9F","pcwl_id":11}) # 11
db.pcwliplist.insert({"ip":"10.0.11.105","node_id":1301,"floor":"W2-9F","pcwl_id":12}) # 12
db.pcwliplist.insert({"ip":"10.0.11.107","node_id":1302,"floor":"W2-9F","pcwl_id":13}) # 13
db.pcwliplist.insert({"ip":"10.0.11.117","node_id":1303,"floor":"W2-9F","pcwl_id":14}) # 14
db.pcwliplist.insert({"ip":"10.0.11.109","node_id":1304,"floor":"W2-9F","pcwl_id":15}) # 15
db.pcwliplist.insert({"ip":"10.0.11.115","node_id":1305,"floor":"W2-9F","pcwl_id":16}) # 16
db.pcwliplist.insert({"ip":"10.0.12.51","node_id":1306,"floor":"W2-9F","pcwl_id":17}) # 17
db.pcwliplist.insert({"ip":"10.0.12.49","node_id":1307,"floor":"W2-9F","pcwl_id":18}) # 18
db.pcwliplist.insert({"ip":"10.0.11.101","node_id":1308,"floor":"W2-9F","pcwl_id":19}) # 19
# db.pcwliplist.insert({"ip":"10.0.11.143","node_id":1309,"floor":"W2-9F","pcwl_id":20}) # 20
db.pcwliplist.insert({"ip":"10.0.11.73","node_id":1310,"floor":"W2-9F","pcwl_id":21}) # 21
db.pcwliplist.insert({"ip":"10.0.11.113","node_id":1311,"floor":"W2-9F","pcwl_id":22}) # 22
db.pcwliplist.insert({"ip":"10.0.11.111","node_id":1312,"floor":"W2-9F","pcwl_id":23}) # 23
db.pcwliplist.insert({"ip":"10.0.11.103","node_id":1313,"floor":"W2-9F","pcwl_id":24}) # 24
db.pcwliplist.insert({"ip":"10.0.11.77","node_id":1287,"floor":"W2-9F","pcwl_id":25}) # 25
db.pcwliplist.insert({"ip":"10.0.12.35","node_id":1350,"floor":"W2-9F","pcwl_id":26}) # 26
db.pcwliplist.insert({"ip":"10.0.12.53","node_id":1351,"floor":"W2-9F","pcwl_id":27}) # 27

# kaiyo
db.pcwliplist.insert({"ip":"10.0.12.135","node_id":9001,"floor":"kaiyo","pcwl_id":1}) # 1
db.pcwliplist.insert({"ip":"10.0.12.91" ,"node_id":9002,"floor":"kaiyo","pcwl_id":2}) # 2
# db.pcwliplist.insert({"ip":"10.0.12.139","node_id":9003,"floor":"kaiyo","pcwl_id":3}) # 3
db.pcwliplist.insert({"ip":"10.0.12.133","node_id":9004,"floor":"kaiyo","pcwl_id":4}) # 4
db.pcwliplist.insert({"ip":"10.0.12.229","node_id":9005,"floor":"kaiyo","pcwl_id":5}) # 5
db.pcwliplist.insert({"ip":"10.0.12.131","node_id":9006,"floor":"kaiyo","pcwl_id":6}) # 6
db.pcwliplist.insert({"ip":"10.0.12.239","node_id":9007,"floor":"kaiyo","pcwl_id":7}) # 7
db.pcwliplist.insert({"ip":"10.0.12.201","node_id":9008,"floor":"kaiyo","pcwl_id":8}) # 8
db.pcwliplist.insert({"ip":"10.0.12.141","node_id":9009,"floor":"kaiyo","pcwl_id":9}) # 9
db.pcwliplist.insert({"ip":"10.0.12.125","node_id":9010,"floor":"kaiyo","pcwl_id":10}) # 10
db.pcwliplist.insert({"ip":"10.0.12.97" ,"node_id":9011,"floor":"kaiyo","pcwl_id":11}) # 11

# print("ip,node_id情報登録完了")