# -*- coding: utf-8 -*-
import urllib.request
import datetime
import sys
import time
import socket
from multiprocessing import Pool
from multiprocessing import Process
import os

# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

db.raw100.remove({})
db.raw100_backup.remove({})
db.rttmp3.remove({})
db.timeoutlog.remove({})