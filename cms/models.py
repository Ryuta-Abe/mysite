# -*- coding: utf-8 -*-
from django.db import models
from mongoengine import *

class Sensor(models.Model):
    '''書籍'''
    sid = models.CharField(u'子機ID', max_length=255)
    box_id = models.CharField(u'親機ID', max_length=255)
    #box_name = models.CharField(u'親機名称', max_length=255)
    sensor_id = models.CharField(u'センサ種類', max_length=255)
    sensor_value = models.CharField(u'計測値', max_length=255)
    #response = models.CharField(u'感知', max_length=255)
    value = models.CharField(u'値', max_length=255)
    #timer = models.CharField(u'計測時間', max_length=255)
    #datetime = models.DateField.auto_now(u'日付時刻')
    datetime = models.DateTimeField(u'日付時刻', blank=True)
    date = models.CharField(u'', max_length=255)
    time = models.CharField(u'値', max_length=255)
    
    def __hash__(self):    # Python2: def __unicode__(self):   def __str__(self)
        return self.id

#初期データ保存用
class initial_db(Document):
    box_id = StringField(max_length=255)
    device_id = IntField()
    sensor_type = StringField(max_length=255)
    sensor_value = StringField(max_length=255)
    date = StringField(max_length=255)
    time = StringField(max_length=255)
    datetime = DateTimeField()

#データリスト用
class Sensor2(Document):
    box_id = StringField(max_length=255)
    device_id = IntField()
    sensor_type = StringField(max_length=255)
    ac = FloatField()
    pos_x = IntField()
    pos_y = IntField()
    ilu = IntField()
    tu = FloatField()
    datetime = DateTimeField()
    date = StringField(max_length=255)
    time = StringField(max_length=255)
    error_flag = BooleanField()
    rssi = FloatField()

class positionset(Document):
    datetime = DateTimeField()
    # position_set =  ReferenceField("Position_Set")
    device_id = IntField()
    pos_x = IntField()
    pos_y = IntField()

#一定時間間隔の気温平均データ
class temp_db(Document):
    device_id = IntField()
    pos_x = IntField()
    pos_y = IntField()
    tu = FloatField()
    date = StringField(max_length=255)
    time = StringField(max_length=255)

#追加更新用 DB
class Sensor3(Document):
    box_id = StringField(max_length=255)
    device_id = IntField()
    sensor_type = StringField(max_length=255)
    ac = FloatField()
    pos_x = IntField()
    pos_y = IntField()
    ilu = IntField()
    tu = FloatField()
    datetime = DateTimeField()
    date = StringField(max_length=255)
    time = StringField(max_length=255)
    error_flag = BooleanField()

#errorデータ保存用
class error_db(Document):
    box_id = StringField(max_length=255)
    device_id = IntField()
    date = StringField(max_length=255)
    time = StringField(max_length=255)
    datetime = DateTimeField()

# PCWLのノード情報
class pcwlnode(Document):
    pcwl_id = IntField()
    pos_x = IntField()
    pos_y = IntField()
    next_id = ListField(IntField())
