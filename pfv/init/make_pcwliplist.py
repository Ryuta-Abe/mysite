# -*- coding: utf-8 -*-
# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

def make_pcwliplist():
    db.pcwliplist.remove() # 一旦DBを空に
    
    # W2-6F
    db.pcwliplist.insert({"ip":"10.0.11.5" ,"parallel_num":11,"floor":"W2-6F","pcwl_id":1}) # 1
    db.pcwliplist.insert({"ip":"10.0.11.27","parallel_num":29,"floor":"W2-6F","pcwl_id":2}) # 2
    db.pcwliplist.insert({"ip":"10.0.11.37","parallel_num":47,"floor":"W2-6F","pcwl_id":3}) # 3
    db.pcwliplist.insert({"ip":"10.0.12.71","parallel_num":65,"floor":"W2-6F","pcwl_id":4}) # 4
    db.pcwliplist.insert({"ip":"10.0.12.79","parallel_num":56,"floor":"W2-6F","pcwl_id":5}) # 5
    db.pcwliplist.insert({"ip":"10.0.12.81","parallel_num":38,"floor":"W2-6F","pcwl_id":6}) # 6
    db.pcwliplist.insert({"ip":"10.0.12.29","parallel_num":20,"floor":"W2-6F","pcwl_id":7}) # 7
    db.pcwliplist.insert({"ip":"10.0.11.21","parallel_num":2,"floor":"W2-6F","pcwl_id":8}) # 8
    db.pcwliplist.insert({"ip":"10.0.11.39","parallel_num":19,"floor":"W2-6F","pcwl_id":9}) # 9
    db.pcwliplist.insert({"ip":"10.0.11.33","parallel_num":37,"floor":"W2-6F","pcwl_id":10}) # 10
    db.pcwliplist.insert({"ip":"10.0.11.31","parallel_num":55,"floor":"W2-6F","pcwl_id":11}) # 11
    db.pcwliplist.insert({"ip":"10.0.11.35","parallel_num":28,"floor":"W2-6F","pcwl_id":12}) # 12
    db.pcwliplist.insert({"ip":"10.0.11.9" ,"parallel_num":10,"floor":"W2-6F","pcwl_id":13}) # 13
    db.pcwliplist.insert({"ip":"10.0.11.15","parallel_num":46,"floor":"W2-6F","pcwl_id":14}) # 14
    db.pcwliplist.insert({"ip":"10.0.11.17","parallel_num":64,"floor":"W2-6F","pcwl_id":15}) # 15
    db.pcwliplist.insert({"ip":"10.0.11.13","parallel_num":73,"floor":"W2-6F","pcwl_id":16}) # 16
    db.pcwliplist.insert({"ip":"10.0.11.19","parallel_num":21,"floor":"W2-6F","pcwl_id":17}) # 17
    db.pcwliplist.insert({"ip":"10.0.11.11","parallel_num":39,"floor":"W2-6F","pcwl_id":18}) # 18
    db.pcwliplist.insert({"ip":"10.0.11.29","parallel_num":57,"floor":"W2-6F","pcwl_id":19}) # 19
    db.pcwliplist.insert({"ip":"10.0.11.7" ,"parallel_num":48,"floor":"W2-6F","pcwl_id":20}) # 20
    db.pcwliplist.insert({"ip":"10.0.12.69","parallel_num":12,"floor":"W2-6F","pcwl_id":21}) # 21
    db.pcwliplist.insert({"ip":"10.0.12.77","parallel_num":30,"floor":"W2-6F","pcwl_id":22}) # 22
    db.pcwliplist.insert({"ip":"10.0.12.67","parallel_num":66,"floor":"W2-6F","pcwl_id":23}) # 23
    db.pcwliplist.insert({"ip":"10.0.12.75","parallel_num":3,"floor":"W2-6F","pcwl_id":24}) # 24
    # db.pcwliplist.insert({"ip":"10.0.1.25","parallel_num":}) # 25
    # db.pcwliplist.insert({"ip":"10.0.1.25","parallel_num":}) # 26
    db.pcwliplist.insert({"ip":"10.0.11.25","parallel_num":1,"floor":"W2-6F","pcwl_id":27}) # 27

    # W2-7F
    db.pcwliplist.insert({"ip":"10.0.11.147","parallel_num":14,"floor":"W2-7F","pcwl_id":1}) # 1
    db.pcwliplist.insert({"ip":"10.0.11.141","parallel_num":32,"floor":"W2-7F","pcwl_id":2}) # 2
    db.pcwliplist.insert({"ip":"10.0.11.149","parallel_num":50,"floor":"W2-7F","pcwl_id":3}) # 3
    db.pcwliplist.insert({"ip":"10.0.11.157","parallel_num":68,"floor":"W2-7F","pcwl_id":4}) # 4
    db.pcwliplist.insert({"ip":"10.0.11.59" ,"parallel_num":59,"floor":"W2-7F","pcwl_id":5}) # 5
    db.pcwliplist.insert({"ip":"10.0.11.51" ,"parallel_num":41,"floor":"W2-7F","pcwl_id":6}) # 6
    db.pcwliplist.insert({"ip":"10.0.11.45" ,"parallel_num":23,"floor":"W2-7F","pcwl_id":7}) # 7
    db.pcwliplist.insert({"ip":"10.0.11.43" ,"parallel_num":5,"floor":"W2-7F","pcwl_id":8}) # 8
    db.pcwliplist.insert({"ip":"10.0.11.41" ,"parallel_num":22,"floor":"W2-7F","pcwl_id":9}) # 9
    db.pcwliplist.insert({"ip":"10.0.11.49" ,"parallel_num":40,"floor":"W2-7F","pcwl_id":10}) # 10
    db.pcwliplist.insert({"ip":"10.0.11.47" ,"parallel_num":58,"floor":"W2-7F","pcwl_id":11}) # 11
    db.pcwliplist.insert({"ip":"10.0.11.153","parallel_num":67,"floor":"W2-7F","pcwl_id":12}) # 12
    db.pcwliplist.insert({"ip":"10.0.11.151","parallel_num":13,"floor":"W2-7F","pcwl_id":13}) # 13
    db.pcwliplist.insert({"ip":"10.0.11.159","parallel_num":49,"floor":"W2-7F","pcwl_id":14}) # 14
    db.pcwliplist.insert({"ip":"10.0.12.33" ,"parallel_num":31,"floor":"W2-7F","pcwl_id":15}) # 15
    db.pcwliplist.insert({"ip":"10.0.12.27" ,"parallel_num":24,"floor":"W2-7F","pcwl_id":16}) # 16
    db.pcwliplist.insert({"ip":"10.0.12.43" ,"parallel_num":42,"floor":"W2-7F","pcwl_id":17}) # 17
    db.pcwliplist.insert({"ip":"10.0.12.39" ,"parallel_num":60,"floor":"W2-7F","pcwl_id":18}) # 18
    # db.pcwliplist.insert({"ip":"10.0.1.25","parallel_num": # 19
    db.pcwliplist.insert({"ip":"10.0.11.57" ,"parallel_num":78,"floor":"W2-7F","pcwl_id":20}) # 20
    db.pcwliplist.insert({"ip":"10.0.12.31" ,"parallel_num":51,"floor":"W2-7F","pcwl_id":21}) # 21
    db.pcwliplist.insert({"ip":"10.0.12.25" ,"parallel_num":15,"floor":"W2-7F","pcwl_id":22}) # 22
    db.pcwliplist.insert({"ip":"10.0.12.41" ,"parallel_num":33,"floor":"W2-7F","pcwl_id":23}) # 23
    db.pcwliplist.insert({"ip":"10.0.11.155","parallel_num":69,"floor":"W2-7F","pcwl_id":24}) # 24
    db.pcwliplist.insert({"ip":"10.0.11.145","parallel_num":4,"floor":"W2-7F","pcwl_id":25}) # 25
    db.pcwliplist.insert({"ip":"10.0.12.47" ,"parallel_num":76,"floor":"W2-7F","pcwl_id":26}) # 26
    db.pcwliplist.insert({"ip":"10.0.12.37" ,"parallel_num":6,"floor":"W2-7F","pcwl_id":27}) # 27

    # W2-8F
    db.pcwliplist.insert({"ip":"10.0.2.88","parallel_num":999,"floor":"W2-8F","pcwl_id":1 }) # 1
    db.pcwliplist.insert({"ip":"10.0.8.92","parallel_num":999,"floor":"W2-8F","pcwl_id":2 }) # 2
    db.pcwliplist.insert({"ip":"10.0.7.82","parallel_num":999,"floor":"W2-8F","pcwl_id":3 }) # 3
    db.pcwliplist.insert({"ip":"10.0.2.82","parallel_num":999,"floor":"W2-8F","pcwl_id":4 }) # 4
    db.pcwliplist.insert({"ip":"10.0.2.254","parallel_num":999,"floor":"W2-8F","pcwl_id":5 }) # 5
    db.pcwliplist.insert({"ip":"10.0.0.166","parallel_num":999,"floor":"W2-8F","pcwl_id":6 }) # 6
    db.pcwliplist.insert({"ip":"10.0.5.10","parallel_num":999,"floor":"W2-8F","pcwl_id":7 }) # 7
    db.pcwliplist.insert({"ip":"10.0.2.164","parallel_num":999,"floor":"W2-8F","pcwl_id":8 }) # 8
    # db.pcwliplist.insert({"ip":"10.0.3.6","parallel_num":999,"floor":"W2-8F","pcwl_id":9 }) # 9
    db.pcwliplist.insert({"ip":"10.0.0.180","parallel_num":999,"floor":"W2-8F","pcwl_id":10}) # 10
    db.pcwliplist.insert({"ip":"10.0.8.74","parallel_num":999,"floor":"W2-8F","pcwl_id":11}) # 11
    db.pcwliplist.insert({"ip":"10.0.2.154","parallel_num":999,"floor":"W2-8F","pcwl_id":12}) # 12
    db.pcwliplist.insert({"ip":"10.0.8.82","parallel_num":999,"floor":"W2-8F","pcwl_id":13}) # 13
    db.pcwliplist.insert({"ip":"10.0.2.80","parallel_num":999,"floor":"W2-8F","pcwl_id":14}) # 14
    db.pcwliplist.insert({"ip":"10.0.0.168","parallel_num":999,"floor":"W2-8F","pcwl_id":15}) # 15
    db.pcwliplist.insert({"ip":"10.0.7.72","parallel_num":999,"floor":"W2-8F","pcwl_id":16}) # 16
    db.pcwliplist.insert({"ip":"10.0.0.136","parallel_num":999,"floor":"W2-8F","pcwl_id":17}) # 17
    db.pcwliplist.insert({"ip":"10.0.7.70","parallel_num":999,"floor":"W2-8F","pcwl_id":18}) # 18
    db.pcwliplist.insert({"ip":"10.0.0.130","parallel_num":999,"floor":"W2-8F","pcwl_id":19}) # 19
    # db.pcwliplist.insert({"ip":"10.0.2.250","parallel_num":999,"floor":"W2-8F","pcwl_id":20}) # 20
    # db.pcwliplist.insert({"ip":"10.0.8.90","parallel_num":999,"floor":"W2-8F","pcwl_id":21}) # 21
    # db.pcwliplist.insert({"ip":"10.0.3.2","parallel_num":999,"floor":"W2-8F","pcwl_id":22}) # 22
    # db.pcwliplist.insert({"ip":"10.0.3.0","parallel_num":999,"floor":"W2-8F","pcwl_id":23}) # 23
    # db.pcwliplist.insert({"ip":"10.0.2.128","parallel_num":999,"floor":"W2-8F","pcwl_id":24}) # 24
    # db.pcwliplist.insert({"ip":"10.0.0.128","parallel_num":999,"floor":"W2-8F","pcwl_id":25}) # 25
    # db.pcwliplist.insert({"ip":"10.0.2.74","parallel_num":999,"floor":"W2-8F","pcwl_id":26}) # 26
    # db.pcwliplist.insert({"ip":"10.0.5.20","parallel_num":999,"floor":"W2-8F","pcwl_id":27}) # 27
    # db.pcwliplist.insert({"ip":"10.0.2.86","parallel_num":999,"floor":"W2-8F","pcwl_id":28}) # 28
    # db.pcwliplist.insert({"ip":"10.0.0.176","parallel_num":999,"floor":"W2-8F","pcwl_id":29}) # 29
    # db.pcwliplist.insert({"ip":"10.0.2.116","parallel_num":999,"floor":"W2-8F","pcwl_id":30}) # 30

    # W2-9F
    db.pcwliplist.insert({"ip":"10.0.11.69","parallel_num":17,"floor":"W2-9F","pcwl_id":1 }) # 1
    db.pcwliplist.insert({"ip":"10.0.11.67","parallel_num":35,"floor":"W2-9F","pcwl_id":2 }) # 2
    db.pcwliplist.insert({"ip":"10.0.11.65","parallel_num":53,"floor":"W2-9F","pcwl_id":3 }) # 3
    db.pcwliplist.insert({"ip":"10.0.11.61","parallel_num":71,"floor":"W2-9F","pcwl_id":4 }) # 4
    db.pcwliplist.insert({"ip":"10.0.11.53","parallel_num":80,"floor":"W2-9F","pcwl_id":5 }) # 5
    db.pcwliplist.insert({"ip":"10.0.11.79","parallel_num":62,"floor":"W2-9F","pcwl_id":6 }) # 6
    db.pcwliplist.insert({"ip":"10.0.11.75","parallel_num":44,"floor":"W2-9F","pcwl_id":7 }) # 7
    db.pcwliplist.insert({"ip":"10.0.11.71","parallel_num":26,"floor":"W2-9F","pcwl_id":8 }) # 8
    db.pcwliplist.insert({"ip":"10.0.11.63","parallel_num":8,"floor":"W2-9F","pcwl_id":9 }) # 9
    # db.pcwliplist.insert({"ip":"10.0.11.55","parallel_num":54,"floor":"W2-9F","pcwl_id":10}) # 10
    db.pcwliplist.insert({"ip":"10.0.11.119","parallel_num":25,"floor":"W2-9F","pcwl_id":11}) # 11
    db.pcwliplist.insert({"ip":"10.0.11.105","parallel_num":61,"floor":"W2-9F","pcwl_id":12}) # 12
    db.pcwliplist.insert({"ip":"10.0.11.107","parallel_num":43,"floor":"W2-9F","pcwl_id":13}) # 13
    db.pcwliplist.insert({"ip":"10.0.11.117","parallel_num":16,"floor":"W2-9F","pcwl_id":14}) # 14
    db.pcwliplist.insert({"ip":"10.0.11.109","parallel_num":79,"floor":"W2-9F","pcwl_id":15}) # 15
    db.pcwliplist.insert({"ip":"10.0.11.115","parallel_num":34,"floor":"W2-9F","pcwl_id":16}) # 16
    db.pcwliplist.insert({"ip":"10.0.12.51","parallel_num":52,"floor":"W2-9F","pcwl_id":17}) # 17
    db.pcwliplist.insert({"ip":"10.0.12.49","parallel_num":27,"floor":"W2-9F","pcwl_id":18}) # 18
    db.pcwliplist.insert({"ip":"10.0.11.101","parallel_num":45,"floor":"W2-9F","pcwl_id":19}) # 19
    # db.pcwliplist.insert({"ip":"10.0.11.143","parallel_num":,"floor":"W2-9F","pcwl_id":20}) # 20
    db.pcwliplist.insert({"ip":"10.0.11.73","parallel_num":72,"floor":"W2-9F","pcwl_id":21}) # 21
    db.pcwliplist.insert({"ip":"10.0.11.113","parallel_num":63,"floor":"W2-9F","pcwl_id":22}) # 22
    db.pcwliplist.insert({"ip":"10.0.11.111","parallel_num":18,"floor":"W2-9F","pcwl_id":23}) # 23
    db.pcwliplist.insert({"ip":"10.0.11.103","parallel_num":36,"floor":"W2-9F","pcwl_id":24}) # 24
    db.pcwliplist.insert({"ip":"10.0.11.77","parallel_num":7,"floor":"W2-9F","pcwl_id":25}) # 25
    db.pcwliplist.insert({"ip":"10.0.12.35","parallel_num":70,"floor":"W2-9F","pcwl_id":26}) # 26
    db.pcwliplist.insert({"ip":"10.0.12.53","parallel_num":9,"floor":"W2-9F","pcwl_id":27}) # 27

    # kaiyo
    db.pcwliplist.insert({"ip":"10.0.12.135","parallel_num":999,"floor":"kaiyo","pcwl_id":1}) # 1
    db.pcwliplist.insert({"ip":"10.0.12.91" ,"parallel_num":999,"floor":"kaiyo","pcwl_id":2}) # 2
    # db.pcwliplist.insert({"ip":"10.0.12.139","parallel_num":999,"floor":"kaiyo","pcwl_id":3}) # 3
    db.pcwliplist.insert({"ip":"10.0.12.133","parallel_num":999,"floor":"kaiyo","pcwl_id":4}) # 4
    db.pcwliplist.insert({"ip":"10.0.12.229","parallel_num":999,"floor":"kaiyo","pcwl_id":5}) # 5
    db.pcwliplist.insert({"ip":"10.0.12.131","parallel_num":999,"floor":"kaiyo","pcwl_id":6}) # 6
    db.pcwliplist.insert({"ip":"10.0.12.239","parallel_num":999,"floor":"kaiyo","pcwl_id":7}) # 7
    db.pcwliplist.insert({"ip":"10.0.12.201","parallel_num":999,"floor":"kaiyo","pcwl_id":8}) # 8
    db.pcwliplist.insert({"ip":"10.0.12.141","parallel_num":999,"floor":"kaiyo","pcwl_id":9}) # 9
    db.pcwliplist.insert({"ip":"10.0.12.125","parallel_num":999,"floor":"kaiyo","pcwl_id":10}) # 10
    db.pcwliplist.insert({"ip":"10.0.12.97" ,"parallel_num":999,"floor":"kaiyo","pcwl_id":11}) # 11

    print("successfully inserted!")

if __name__ == '__main__':
    make_pcwliplist()