#!/usr/bin/env python
# GoodFET Nordic RF Radio Client
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, time, string, cStringIO, struct, glob, serial, os;

from GoodFET import GoodFET;

class GoodFETNRF(GoodFET):
    NRFAPP=0x50;
    def NRFsetup(self):
        """Move the FET into the NRF application."""
        self.writecmd(self.NRFAPP,0x10,0,self.data); #NRF/SETUP
        
    def NRFtrans8(self,byte):
        """Read and write 8 bits by NRF."""
        data=self.NRFtrans([byte]);
        return ord(data[0]);
    
    def NRFtrans(self,data):
        """Exchange data by NRF."""
        self.data=data;
        self.writecmd(self.NRFAPP,0x00,len(data),data);
        return self.data;
    
    def peek(self,reg,bytes=1):
        """Read an NRF Register.  For long regs, result is flipped."""
        data=[reg,0,0,0,0,0];
        self.writecmd(self.NRFAPP,0x02,len(data),data);
        toret=0;
        for i in range(0,bytes):
            toret=toret|(ord(self.data[i+1])<<(8*i));
        return toret;
    def poke(self,reg,val,bytes=1):
        """Write an NRF Register."""
        data=[reg];
        for i in range(0,bytes):
            data=data+[(val>>(8*i))&0xFF];
        self.writecmd(self.NRFAPP,0x03,len(data),data);
        if self.peek(reg,bytes)!=val:
            print "Warning, failed to set register %02x." %reg;
        return;
    
    def status(self):
        """Read the status byte."""
        status=self.peek(0x07);
        print "Status=%02x" % status;
    
    #Radio stuff begins here.
    def RF_freq(self,frequency):
        """Set the frequency in Hz."""
        
        #On the NRF24L01+, register 0x05 is the offset in
        #MHz above 2400.
        
        mhz=frequency/1000000-2400;
        print "Setting channel %i." % mhz 
        self.poke(0x05,mhz);
    def RF_getsmac(self):
        """Return the source MAC address."""
        
        #Register 0A is RX_ADDR_P0, five bytes.
        mac=self.peek(0x0A, 5);
        return mac;
    def RF_setsmac(self,mac):
        """Set the source MAC address."""
        
        #Register 0A is RX_ADDR_P0, five bytes.
        self.poke(0x0A, mac, 5);
        return mac;
    def RF_gettmac(self):
        """Return the target MAC address."""
        
        #Register 0x10 is TX_ADDR, five bytes.
        mac=self.peek(0x0A, 5);
        return mac;
    def RF_settmac(self,mac):
        """Set the target MAC address."""
        
        #Register 0x10 is TX_ADDR, five bytes.
        self.poke(0x10, mac, 5);
        return mac;
    def RF_rxpacket(self):
        """Get a packet from the radio.  Returns None if none is waiting."""
        if self.peek(0x07) & 0x40:
            #Packet has arrived.
            self.writecmd(self.NRFAPP,0x80,0,None); #RX Packet
            data=self.data;
            self.poke(0x07,0x40);#clear bit.
            return data;
        elif self.peek(0x07)==0:
            self.writecmd(self.NRFAPP,0x82,0,None); #Flush
            self.poke(0x07,0x40);#clear bit.
        return None;
