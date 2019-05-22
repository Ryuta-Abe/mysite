# MongoDB table definition

## tmpcol 
### MACアドレス・取得時間をキーに全ノードのdbmを集計したコレクション
```
{
    "_id" : {
            "mac" : "d4:38:9c:34:e5:d7",
            "get_time_no" : ISODate("2018-01-31T15:06:10Z")
    },
    "nodelist" : [
            {
                    "dbm" : -85,
                    "ip" : "10.0.11.47"
            },
            {
                    "dbm" : -92,
                    "ip" : "10.0.11.107"
            }
    ]
}

get_start_endにおいてnodelistを変換処理
    "nodelist" : [
            {
                    "rssi" : -85,
                    "floor" : "W2-7F"
                    "pcwl_id" : 11
            }, ...
    ]

```


## pastdata
###　MACアドレス毎の過去データ
### nodecnt_dict: 各ノードの出現回数
### pastlist: 過去の存在位置
```
{
        "mac" : "0a:08:0b:3a:70:02",
        "update_dt" : ISODate("2018-01-31T13:30:15Z"),
        "nodecnt_dict" : {
                "W2-6F" : {
                        "1" : 0,
                        "2" : 0,
                        "3" : 0,
                        "4" : 0,
                        "5" : 0,
                        "6" : 0,
                        "7" : 0,
                        "8" : 0,
                        "9" : 1,
                        "10" : 0,
                        "11" : 0,
                        "12" : 1,
                        "13" : 0,
                        "14" : 1,
                        "15" : 0,
                        "16" : 0,
                        "17" : 0,
                        "18" : 0,
                        "19" : 0,
                        "20" : 0,
                        "21" : 0,
                        "22" : 0,
                        "23" : 0,
                        "24" : 0,
                        "25" : 0,
                        "26" : 0,
                        "27" : 0
                },
                "W2-7F" : {
                        "1" : 0,
                        "2" : 0,
                        "3" : 0,
                        "4" : 0,
                        "5" : 0,
                        "6" : 0,
                        "7" : 0,
                        "8" : 0,
                        "9" : 0,
                        "10" : 0,
                        "11" : 0,
                        "12" : 0,
                        "13" : 0,
                        "14" : 0,
                        "15" : 0,
                        "16" : 0,
                        "17" : 0,
                        "18" : 0,
                        "19" : 0,
                        "20" : 0,
                        "21" : 0,
                        "22" : 0,
                        "23" : 0,
                        "24" : 0,
                        "25" : 0,
                        "26" : 0,
                        "27" : 0
                },
                "W2-9F" : {
                        "1" : 0,
                        "2" : 0,
                        "3" : 0,
                        "4" : 0,
                        "5" : 0,
                        "6" : 0,
                        "7" : 0,
                        "8" : 0,
                        "9" : 0,
                        "10" : 0,
                        "11" : 0,
                        "12" : 0,
                        "13" : 0,
                        "14" : 0,
                        "15" : 0,
                        "16" : 0,
                        "17" : 0,
                        "18" : 0,
                        "19" : 0,
                        "20" : 0,
                        "21" : 0,
                        "22" : 0,
                        "23" : 0,
                        "24" : 0,
                        "25" : 0,
                        "26" : 0,
                        "27" : 0
                }
        },
        "pastlist" : [
                {
                        "dt" : ISODate("2018-01-31T13:30:10Z"),
                        "start_node" : {
                                "floor" : "W2-6F",
                                "pcwl_id" : 14,
                                "rssi" : -55
                        },
                        "node" : [ ],
                        "alive" : false,
                        "arrive_intersection" : false
                },
                {
                        "dt" : ISODate("2018-01-31T13:30:05Z"),
                        "start_node" : {
                                "floor" : "W2-6F",
                                "pcwl_id" : 14,
                                "rssi" : -55
                        },
                        "node" : [ ],
                        "alive" : false,
                        "arrive_intersection" : false
                },
                {
                        "dt" : ISODate("2018-01-31T13:30:00Z"),
                        "start_node" : {
                                "floor" : "W2-6F",
                                "pcwl_id" : 14,
                                "rssi" : -55
                        },
                        "node" : [
                                {
                                        "floor" : "W2-6F",
                                        "pcwl_id" : 14,
                                        "rssi" : -55
                                },
                                {
                                        "floor" : "W2-6F",
                                        "pcwl_id" : 12,
                                        "rssi" : -56
                                },
                                {
                                        "floor" : "W2-6F",
                                        "pcwl_id" : 9,
                                        "rssi" : -60
                                }
                        ],
                        "alive" : true,
                        "arrive_intersection" : false
                },
                {
                        "dt" : ISODate("2018-01-31T13:30:15Z"),
                        "start_node" : {
                                "floor" : "W2-6F",
                                "pcwl_id" : 14,
                                "rssi" : -55
                        },
                        "node" : [ ],
                        "alive" : false,
                        "arrive_intersection" : false
                }
        ]
}
```

## floor_analyze
```
{
        "floor" : "W2-6F",
        "pcwl_id" : 20,
        "go" : {
                "total" : 0,
                "19" : 0,
                "21" : 0,
                "22" : 0
        },
        "come" : {
                "total" : 0,
                "19" : 0,
                "21" : 0,
                "22" : 0
        },
        "transition" : {
                "19" : {
                        "total" : 0,
                        "18" : 0,
                        "20" : 0
                },
                "21" : {
                        "total" : 0,
                        "20" : 0
                },
                "22" : {
                        "total" : 0,
                        "5" : 0,
                        "20" : 0
                }
        }
}



```

{
        "_id" : ObjectId("5c46c6034eadf75b2891b087"),
        "query" : [
                1,
                3
        ],
        "dlist" : [
                [
                        {
                                "distance" : 72.80109889280519,
                                "direction" : [
                                        1,
                                        2
                                ]
                        },
                        {
                                "distance" : 75.16648189186454,
                                "direction" : [
                                        2,
                                        3
                                ]
                        }
                ]
        ],
        "floor" : "W2-6F"
}

## pcwlroute
### 全経路に対して、構成する子経路とその距離
```
{
        "query" : [
                1,
                3
        ],
        "dlist" : [
                [
                        {
                                "distance" : 72.80109889280519,
                                "direction" : [
                                        1,
                                        2
                                ]
                        },
                        {
                                "distance" : 75.16648189186454,
                                "direction" : [
                                        2,
                                        3
                                ]
                        }
                ]
        ],
        "floor" : "W2-6F"
}

```

## pfvmacinfo
### 各MACアドレス・取得時間に対応する移動経路
```
{
        "datetime" : ISODate("2018-12-26T01:35:25Z"),
        "mac" : "00:11:81:10:01:1b",
        "route" : [
                [
                        12,
                        26
                ],
                [
                        26,
                        9
                ]
        ],
        "floor" : "W2-7F"
}


```

## pfvstaymacinfo
### 各MACアドレス・取得時間に対応する滞留位置
```
{
        "datetime" : ISODate("2018-12-26T01:35:15Z"),
        "mac" : "38:78:62:0c:b5:13",
        "pcwl_id" : 25,
        "floor" : "W2-7F"
}
```