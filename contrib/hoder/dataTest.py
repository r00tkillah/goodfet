#!/usr/bin/env python
# Chris Hoder
# 1/11/2012

import MySQLdb
import sys
import csv
from DataManage import *


#print 0x0f>>3

#tests the DataManage.py class
dataM = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table="vue2")
#parsed = dataM.parseMessageInt([ 134, 64, 255, 253, 8, 128, 0, 250, 0, 31, 255, 255, 63])

#print parsed

dataM.uploadData("./data/brights_on_off.csv")
