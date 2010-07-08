#!/usr/bin/env python
# GoodFET EM260 Radio Client
# 
# (C) 2010 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

# The EM260 is almost textbook SPI, except that the response cannot be
# read until after the nHOST_INT pin of the EM260 drops low and a dummy
# byte is read.  That is, the sequence will look like the following:

# Transmit Host->Slave Data
# while(nHOST_INT); //Sleep until ready.
# Recv Dummy Byte
# Recv Slave->Host Data

# The delay is mandatory.

import sys, time, string, cStringIO, struct, glob, serial, os;

from GoodFETSPI import GoodFETSPI;

class GoodFETEM260(GoodFETSPI):
    EM260APP=0x01;
    seq=0;
    def EM260trans(self,data):
        """Exchange data by EM260 SPI. (Slightly nonstandard.)"""
        self.data=data;
        self.writecmd(0x01,0x82,len(data),data);
        return self.data;
    
    
    def peek8(self,adr):
        """Read a byte from the given address."""
        data=self.EM260trans([0xfe,0x01,self.seq,0x00,
                            0x49,
                            0xA7]);
        s="";
        for foo in data:
            s=s+"%02x " % ord(foo);
        print s;
        
        return ord(data[0]);
    def info(self):
        """Read the info bytes."""
        #data=self.EM260trans([0x0A,0xA7]); 
        #data=self.EM260trans([0xFE,0x04,
        #                      0x00,0x00,0x00,0x02,
        #                      0xA7]); 
        data=self.EM260trans([0x0B,0xA7]);
        
        #data=self.EM260trans([]);
        
        #data=self.EM260trans([0x0B,0x0B,0x0B,0x0B,0xA7]);
        
        s="";
        for foo in data:
            s=s+"%02x " % ord(foo);
        print s;
        
