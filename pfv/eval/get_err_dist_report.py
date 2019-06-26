# -*- coding: utf-8 -*-
from pymongo import *
import os

file_name = "err_dist_report(w mid)_fix.csv"
os.command("mongoexport -d nm4bd -c examine_route --type=csv -o " + file_name + " -f 'err_dist'")

