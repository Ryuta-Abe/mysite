# -*- coding: utf-8 -*-
from django.forms import ModelForm
from cms.models import Sensor

class SensorForm(ModelForm):
    '''書籍のフォーム'''
    class Meta:
        model = Sensor
        fields = ('sid', 'box_id', 'sensor_id', 'sensor_value', 'value', 'datetime' )
    """    
    box_id = models.CharField(u'親機ID', max_length=255)
    box_name = models.CharField(u'親機名称', max_length=255)
    sensor_id = models.CharField(u'センサ種類', max_length=255)
    sensor_value = models.CharField(u'値', max_length=255)
    response = models.CharField(u'感知', max_length=255)
    value = models.CharField(u'値', max_length=255)
    timer = models.CharField(u'計測時間', max_length=255)
    #datetime = models.DateField.auto_now(u'日付時刻')
    datetime = models.DateTimeField(u'日付時刻', blank=True)
    """