#!/usr/bin/env python
# GoodFET Windows Installer
# 
# Written poorly by Q - <q@theqlabs.com>
#
# This code is being rewritten and refactored.  You've been warned!

from distutils.core import setup
import py2exe, sys, os

setup(console=['goodfet.bsl'])
