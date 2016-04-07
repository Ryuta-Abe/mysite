# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from cms import views

urlpatterns = patterns('',
    url(r'^data_list2/$', views.data_list2, name='data_list2'),   
    url(r'^data_list2/limit=(?P<limit>\d+)/$', views.data_list2, name='data_list2'),
    url(r'^data_list2/limit=(?P<limit>\d+)/datetime=(?P<date_time>\w+)/$', views.data_list2, name='data_list2'),   # 加速度
    url(r'^data_list3/$', views.data_list, name='data_list3'),   # 照度
    url(r'^data_list4/$', views.data_list, name='data_list4'),   # 赤外線
    url(r'^data_list5/$', views.data_list, name='data_list5'),   # test
    url(r'^data_list9/$', views.data_list, name='data_list9'),   # 加速度　test
    url(r'^data_list10/$', views.data_list, name='data_list10'),   # 加速度　test
    url(r'^data_list11/$', views.data_list, name='data_list11'),   # 照度グラフ
    url(r'^data_list12/$', views.data_list, name='data_list12'),   # 赤外線サーモグラフィー
    url(r'^data_list13/$', views.data_list, name='data_list13'),   # 加速度　積み棒グラフ練習
    url(r'^data_list14/$', views.data_list, name='data_list14'),   # 加速度　積み棒グラフ
    url(r'^data_list15/$', views.data_list, name='data_list15'),   # 加速度　棒グラフ　+-あり
    url(r'^data_list16/$', views.data_list, name='data_list16'),   # 
    url(r'^data_list17/$', views.data_list, name='data_list17'),   # 
    url(r'^data_list18/$', views.data_list, name='data_list18'),   # 気温
     
    url(r'^d3jstest/$', views.d3jstest, name=''),   #練習用

    url(r'^response_json/$', views.response_json, name='response_json'),   # JSONを返すURL
    url(r'^response_json/datetime=(?P<date_time>\d+)/$', views.response_json, name='response_json'),   # JSONを返すURL

    url(r'^save_db/$', views.save_db, name='save_db'), #データ統合・登録
    url(r'^update_db/$', views.update_db, name='update_db'), #データ更新・追加
    url(r'^save_db_heat/$', views.save_db_heat, name='save_db_heat'), #データ登録(1hごとの温度データ)
    # url(r'^save_initial_data/$', views.save_initial_data, name='save_initial_data'), #データ登録(初期データ)

    url(r'^sensor_map/$', views.sensor_map, name='sensor_map'), #センサーマップ
    url(r'^sensor_map/datetime=(?P<date_time>\d+)/$', views.sensor_map, name='sensor_map'),
    url(r'^sensor_map/datetime=(?P<date_time>\d+)/type=(?P<type>\d{2})/$', views.sensor_map, name='sensor_map'),

    url(r'^sensor_graph/$', views.sensor_graph, name='sensor_graph'),   # センサーグラフ
    url(r'^sensor_graph/limit=(?P<limit>\d+)/datetime=(?P<date_time>\d+)/type=(?P<type>\w+)/$', views.sensor_graph, name='sensor_graph'),
    url(r'^sensor_graph_json/$', views.sensor_graph_json, name='sensor_graph_json'),
    url(r'^sensor_graph_json/limit=(?P<limit>\d+)/datetime=(?P<date_time>\d+)/type=(?P<type>\w+)/$', views.sensor_graph_json, name='sensor_graph_json'),
    url(r'^sensor_graph2/$', views.sensor_graph2, name='sensor_graph2'),   # センサーグラフ
    url(r'^sensor_graph2/limit=(?P<limit>\d+)/datetime=(?P<date_time>\d+)/type=(?P<type>\w+)/$', views.sensor_graph2, name='sensor_graph2'),


    # データ一覧
    url(r'^data_list/$', views.data_list, name='data_list'),   
    url(r'^data_list/limit=(?P<limit>\d+)/$', views.data_list, name='data_list'),
    url(r'^data_list/limit=(?P<limit>\d+)/datetime=(?P<date_time>\w+)/$', views.data_list, name='data_list'),
    # データ件数確認用
    url(r'^data_check/$', views.data_check, name='data_check'),
    url(r'^data_check/datetime=(?P<date_time>\w+)/$', views.data_check, name='data_check'),

    # 位置情報編集関係
    url(r'^position_list/$', views.position_list, name='position_list'),
    url(r'^position_add/$', views.position_add, name='position_add'),
    url(r'^position_edit/$', views.position_edit, name='position_edit'),
    url(r'^position_edit/datetime=(?P<date_time>\d+)/$', views.position_edit, name='position_edit'),
    url(r'^position_delete/$', views.position_delete, name='position_delete'),
    url(r'^position_delete/datetime=(?P<date_time>\d+)/$', views.position_delete, name='position_delete'),
    url(r'^position_delete/datetime=(?P<date_time>\d+)/id=(?P<id>\d+)/$', views.position_delete, name='position_delete'),
    url(r'^position_save/$', views.position_save, name='position_save'),
    url(r'^position_save/datetime=(?P<date_time>\d+)/id=(?P<id>\d+)/pos_x=(?P<pos_x>\d+)/pos_y=(?P<pos_y>\d+)/$', views.position_save, name='position_save'),

    #英語版
    url(r'^sensor_map_en/$', views.sensor_map_en, name='sensor_map_en'),   # センサーマップ英語版
    url(r'^sensor_map_en/datetime=(?P<date_time>\d+)/$', views.sensor_map_en, name='sensor_map_en'),
    url(r'^sensor_map_en/datetime=(?P<date_time>\d+)/type=(?P<type>\d{2})/$', views.sensor_map_en, name='sensor_map_en'),
    url(r'^sensor_graph_en/$', views.sensor_graph_en, name='sensor_graph_en'),   # センサーグラフ英語版
    url(r'^sensor_graph_en/limit=(?P<limit>\d+)/datetime=(?P<date_time>\d+)/type=(?P<type>\w+)/$', views.sensor_graph_en, name='sensor_graph_en'),

    # csv関係
    url(r'^csv_list/$', views.csv_list, name='csv_list'),

    # SDtest
    url(r'^sdtest/$', views.sdtest, name='sdtest'),   
  
)