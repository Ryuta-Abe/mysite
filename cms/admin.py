# -*- coding: utf-8 -*-
from django.contrib import admin
from cms.models import Sensor #Impression

#admin.site.register(Sensor)
#admin.site.register(Impression)

class SensorAdmin(admin.ModelAdmin):
    list_display = ('sid', 'box_id', 'sensor_id', 'datetime')  # 一覧に出したい項目
    #list_display_links = ('id', 'box_name',)  # 修正リンクでクリックできる項目
admin.site.register(Sensor, SensorAdmin)

"""
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'publisher', 'page',)  # 一覧に出したい項目
    list_display_links = ('id', 'name',)  # 修正リンクでクリックできる項目
admin.site.register(Book, BookAdmin)
"""
"""
class ImpressionAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment',)
    list_display_links = ('id', 'comment',)
admin.site.register(Impression, ImpressionAdmin)
"""