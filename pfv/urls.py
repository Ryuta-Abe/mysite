# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from pfv import views, make_pfvinfo, aggregate, get_start_end, bookmark_edit

urlpatterns = patterns('',

    url(r'^pfv_map/$', views.pfv_map, name='pfv_map'), #pfvマップ
    url(r'^pfv_map_json/$', views.pfv_map_json, name='pfv_map_json'), #pfvマップ用JSON
    url(r'^pfv_graph/$', views.pfv_graph, name='pfv_graph'),   # pfvグラフ
    url(r'^stay_graph/$', views.stay_graph, name='stay_graph'),   # stayグラフ
    url(r'^pfv_heatmap/$', views.pfv_heatmap, name='pfv_heatmap'), #heatmap
    url(r'^pfv_heatmap_json/$', views.pfv_heatmap_json, name='pfv_heatmap_json'), #heatmap用json

    url(r'^bookmark_edit/$', bookmark_edit.bookmark_edit, name='bookmark_edit'), # ブックマークの編集

    url(r'^aggregate/$', aggregate.aggregate_data, name='aggregate_data'),
    url(r'^get_start_end/$', get_start_end.get_start_end, name='get_start_end'),
    url(r'^XXX/$', make_pfvinfo.XXX, name='XXX'),
    url(r'^mac_trace/$', views.mac_trace, name='mac_trace'), #mac_trace
    url(r'^mac_trace_json/$', views.mac_trace_json, name='mac_trace_json'),
    # # データ一覧
    url(r'^data_list/$', views.data_list, name='data_list'),
    url(r'^data_list/limit=(?P<limit>\d+)/$', views.data_list, name='data_list'),
    url(r'^data_list/limit=(?P<limit>\d+)/datetime=(?P<date_time>\w+)/$', views.data_list, name='data_list'),

    url(r'^analyze/$', views.analyze_direction, name='analyze_direction'),
    url(r'^analyze/mac=(?P<mac>[\w,\W]*)/$', views.analyze_direction, name='analyze_direction'),
    url(r'^analyze/limit=(?P<limit>\d+)/$', views.analyze_direction, name='analyze_direction'),
    url(r'^analyze/limit=(?P<limit>\d+)/datetime=(?P<date_time>\w+)/$', views.analyze_direction, name='analyze_direction'),

)