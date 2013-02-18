#!/usr/bin/env python
# GoodFET I2C and I2Ceeprom Client Library
# 
# Pre-alpha.  You've been warned!

#import sys, time, string, cStringIO, struct, glob, serial, os

from GoodFET import GoodFET

class GoodFETI2C(GoodFET):
    def I2Csetup(self):
        """Move the FET into the I2C application."""
        self.writecmd(0x02,0x10)
        
    def I2Cstart(self):
	"""Produce Start condition on I2C bus"""
        self.writecmd(0x02,0x20)
    def I2Cstop(self):
	"""Produce Stop condition on I2C bus"""
        self.writecmd(0x02,0x21)
    def I2Cread(self,count=1):
        """Read data from I2C."""
        self.writecmd(0x02,0x00,1,[count])
    def I2Cwritebytes(self,data):
	"""Write multiple bytes to I2C."""
        self.writecmd(0x02,0x01,len(data),data)
    def I2Cwritebyte(self,val):
	"""Write a single byte to I2C."""
        self.I2Cwritebytes([val])
    def I2Ctrans(self,readcount,data):
	"""Use PEEK to do a multi-start transaction"""
	return self.writecmd(0x02,0x02,len(data)+1,[readcount]+data)
