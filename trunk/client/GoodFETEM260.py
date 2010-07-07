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
    def peek8(self,adr):
        """Read a byte from the given address."""
        data=self.SPItrans([0xfe,0x01,0x00,
                            0x49,
                            0xA7,0,0,0,0,0,0,0,0]);
        return ord(data[7]);
    def poke8(self,adr, byte):
        """Poke a byte to the given address."""
    def info(self):
        """Read the info bytes."""
        data=self.SPItrans([0x0B,0xA7,
                            0xFF,
                            0xFF,0xFF,0xFF,     #00 02 A7
                            0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0,
                            0,0,0,0,0,0,0,0,0,0
                            ]); 
        for foo in data:
            print "%02x" % ord(foo);
