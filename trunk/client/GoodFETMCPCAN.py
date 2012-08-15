#!/usr/bin/env python
# GoodFET MCP2515 CAN Bus Client
# 
# (C) 2012 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!
#

# The MCP2515 is a CAN Bus to SPI adapter from Microchip Technology,
# as used in the Goodthopter series of boards.  It requires a separate
# chip for voltage level conversion, such as the MCP2551.

import sys, time, string, cStringIO, struct, glob, os;

from GoodFETSPI import GoodFETSPI;

class GoodFETMCPCAN(GoodFETSPI):
    def MCPsetup(self):
        """Sets up the ports."""
        self.SPIsetup();
        self.MCPreset(); #Reset the chip.
        
    def MCPreset(self):
        """Reset the MCP2515 chip."""
        self.SPItrans([0xC0]);
    def MCPrxstatus(self):
        """Reads the RX Status by the SPI verb of the same name."""
        data=self.SPItrans([0xB0,0x00]);
        return ord(data[1]);
    def MCPreadstatus(self):
        """Reads the RX Status by the SPI verb of the same name."""
        data=self.SPItrans([0xA0,0x00]);
        return ord(data[1]);
    def peek8(self,adr):
        """Read a byte from the given address.  Untested."""
        data=self.SPItrans([0x03,adr&0xFF,00]);
        return ord(data[2]);
    
    def poke8(self,adr,val):
        """Poke a value into RAM.  Untested"""
        self.SPItrans([0x02,adr&0xFF,val&0xFF]);
        return val;
    def rand16(self):
        """Read a random 16-bit word."""
        
        data=self.EZSPtrans([0x49]);
        if data==None:
            print "Insufficient random data.";
            return 0;
        return ord(data[6])+(ord(data[7])<<8);

    def info(self):
        """Read the info bytes."""
        print "Ember EM26 Z-Stack SPI Module.";
        version=self.EM260spiversion();
        status=self.EM260spistatus();
        print "Version: %i" % (version); 
        print "Status:  %s" % (["dead","alive"][status]);
        print ""
        self.setVersion();
        print "Node ID: %04x" % (self.getNodeID());
        print "Connected to %2i neighbors." % self.neighborCount();
