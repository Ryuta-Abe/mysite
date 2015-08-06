# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from pfv import views

urlpatterns = patterns('',
     
    # url(r'^d3jstest/$', views.d3jstest, name=''),   #練習用

    # url(r'^response_json/$', views.response_json, name='response_json'),   # JSONを返すURL
    # url(r'^response_json/datetime=(?P<date_time>\d+)/$', views.response_json, name='response_json'),   # JSONを返すURL

    # url(r'^save_db/$', views.save_db, name='save_db'), #データ統合・登録
    # url(r'^update_db/$', views.update_db, name='update_db'), #データ更新・追加
    # url(r'^save_db_heat/$', views.save_db_heat, name='save_db_heat'), #データ登録(1hごとの温度データ)
    # # url(r'^save_initial_data/$', views.save_initial_data, name='save_initial_data'), #データ登録(初期データ)

    # url(r'^sensor_map/$', views.sensor_map, name='sensor_map'), #センサーマップ
    # url(r'^sensor_map/datetime=(?P<date_time>\d+)/$', views.sensor_map, name='sensor_map'),
    # url(r'^sensor_map/datetime=(?P<date_time>\d+)/type=(?P<type>\d{2})/$', views.sensor_map, name='sensor_map'),

    # url(r'^sensor_graph/$', views.sensor_graph, name='sensor_graph'),   # センサーグラフ
    # url(r'^sensor_graph/limit=(?P<limit>\d+)/datetime=(?P<date_time>\d+)/type=(?P<type>\w+)/$', views.sensor_graph, name='sensor_graph'),

    # # データ一覧
    url(r'^data_list/$', views.data_list, name='data_list'),   
    url(r'^data_list/limit=(?P<limit>\d+)/$', views.data_list, name='data_list'),
    url(r'^data_list/limit=(?P<limit>\d+)/datetime=(?P<date_time>\w+)/$', views.data_list, name='data_list'),
    # # データ件数確認用
    # url(r'^data_check/$', views.data_check, name='data_check'),
    # url(r'^data_check/datetime=(?P<date_time>\w+)/$', views.data_check, name='data_check'),

    # #英語版
    # url(r'^sensor_map_en/$', views.sensor_map_en, name='sensor_map_en'),   # センサーマップ英語版
    # url(r'^sensor_map_en/datetime=(?P<date_time>\d+)/$', views.sensor_map_en, name='sensor_map_en'),
    # url(r'^sensor_map_en/datetime=(?P<date_time>\d+)/type=(?P<type>\d{2})/$', views.sensor_map_en, name='sensor_map_en'),
    # url(r'^sensor_graph_en/$', views.sensor_graph_en, name='sensor_graph_en'),   # センサーグラフ英語版
    # url(r'^sensor_graph_en/limit=(?P<limit>\d+)/datetime=(?P<date_time>\d+)/type=(?P<type>\w+)/$', views.sensor_graph_en, name='sensor_graph_en'),
  
)