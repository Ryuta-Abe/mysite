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
```
### get_start_endにおいて利用しやすいように変換処理
```
{
    "_id" : {
            "mac" : "d4:38:9c:34:e5:d7",
            "get_time_no" : ISODate("2018-01-31T15:06:10Z")
    },
    "nodelist" : [
            {
                    "rssi" : -85,
                    "floor" : "W2-7F"
                    "pcwl_id" : 11
            }, ...
    ]
}

※ここで、node情報を{"rssi" : -85,"floor" : "W2-7F","pcwl_id" : 11}のように定義する


```


## pastdata
###　MACアドレス毎の過去データ
### nodecnt_dict: 各ノードの直近30秒以内での出現回数
### pastlist: 過去の存在位置
```
{
        "mac" : "0a:08:0b:3a:70:02",
        "update_dt" : ISODate("2018-01-31T13:30:15Z"),
        "nodecnt_dict" : {
                "W2-6F" : {
                        "1" : 0,
                        "2" : 0,
                        ...,
                        "27" : 1
                },
                "W2-7F" : {
                        "1" : 0,
                        "2" : 0,
                        ...,
                        "27" : 1
                },
                "W2-9F" : {
                        "1" : 0,
                        "2" : 0,
                        ...,
                        "27" : 1
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
### (datetime - min_interval) ~ datetimeまでの移動経路
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

## qstaymacinfo
### 各MACアドレス・取得時間に対応する滞留位置
```
{
        "datetime" : ISODate("2018-12-26T01:35:15Z"),
        "mac" : "38:78:62:0c:b5:13",
        "pcwl_id" : 25,
        "floor" : "W2-7F"
}
```