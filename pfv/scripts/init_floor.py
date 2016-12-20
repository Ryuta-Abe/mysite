# -*- coding: utf-8 -*-
import os
from make_pcwliplist import *
from make_pcwlnode import *
from save_pcwl_route import *


if __name__ == '__main__':
    make_pcwliplist()
    make_pcwlnode()
    print("Please execute 'python3 ./save_pcwl_route.py'")
    # save_route()
    # os.system("python3 save_pcwl_route.py")
