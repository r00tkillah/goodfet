#!/usr/bin/env python
# GoodFET SPI and SPIFlash Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, time, string, cStringIO, struct, glob, serial, os;

from GoodFET import GoodFET;

class GoodFETAVR(GoodFET):
    AVRAPP=0x32;
    
    def setup(self):
        """Move the FET into the SPI application."""
        self.writecmd(self.AVRAPP,0x10,0,self.data); #SPI/SETUP
    
    def trans(self,data):
        """Exchange data by AVR.
        Input should probably be 4 bytes."""
        self.data=data;
        self.writecmd(self.AVRAPP,0x00,len(data),data);
        return self.data;

    def start(self):
        """Start the connection."""
        self.writecmd(self.AVRAPP,0x20,0,None);

    def identstr(self):
        """Return an identifying string."""
        self.writecmd(self.AVRAPP,0x83,0,None);
        return "AVR(%02x)" % ord(self.data[0]);
