# -*- coding: utf-8 -*-
# 参照dir
dir_list = ["eval","debug","etc","init","rt","util"]

### 以下4行を実行する.pyファイルに追記する ###
# import os, sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
# from env import Env
# Env()

import sys, os
class Env():
    """
    環境変数を一括追加するクラス
    """
    def __init__(self):
        for dir_name in dir_list:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/"+dir_name+"/")
