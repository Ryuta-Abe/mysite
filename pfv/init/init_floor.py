# -*- coding: utf-8 -*-
# import Env
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()

from make_pcwliplist import *
from make_pcwlnode import *
from make_pcwlroute import *


if __name__ == '__main__':
    make_pcwliplist()
    make_pcwlnode()
    make_pcwlroute()
    # print("Please execute 'python3 ./save_pcwl_route.py'")
    # save_route()
    # os.system("python3 save_pcwl_route.py")
