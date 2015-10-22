# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from pfv import views, make_pfvinfo, aggregate, analyze, get_start_end

urlpatterns = patterns('',

    url(r'^pfv_map/$', views.pfv_map, name='pfv_map'), #pfvマップ
    url(r'^pfv_map_json/$', views.pfv_map_json, name='pfv_map_json'), #pfvマップ用JSON
    url(r'^pfv_graph/$', views.pfv_graph, name='pfv_graph'),   # pfvグラフ
    url(r'^stay_graph/$', views.stay_graph, name='stay_graph'),   # stayグラフ

    url(r'^aggregate/$', aggregate.aggregate_data, name='aggregate_data'),
    url(r'^analyze/$', analyze.analyze_direction, name='analyze_direction'),
    url(r'^get_start_end/$', get_start_end.get_start_end, name='get_start_end'),
    url(r'^XXX/$', make_pfvinfo.XXX, name='XXX'),

    # # データ一覧
    url(r'^data_list/$', views.data_list, name='data_list'),
    url(r'^data_list/limit=(?P<limit>\d+)/$', views.data_list, name='data_list'),
    url(r'^data_list/limit=(?P<limit>\d+)/datetime=(?P<date_time>\w+)/$', views.data_list, name='data_list'),

)