#!/usr/bin/env python
# GoodFET Chipcon RF Radio Client
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, time, string, cStringIO, struct, glob, serial, os;

from GoodFET import GoodFET;

class GoodFETCCSPI(GoodFET):
    CCSPIAPP=0x51;
    def setup(self):
        """Move the FET into the CCSPI application."""
        self.writecmd(self.CCSPIAPP,0x10,0,self.data); #CCSPI/SETUP
        
    def trans8(self,byte):
        """Read and write 8 bits by CCSPI."""
        data=self.CCSPItrans([byte]);
        return ord(data[0]);
    
    def trans(self,data):
        """Exchange data by CCSPI."""
        self.data=data;
        self.writecmd(self.CCSPIAPP,0x00,len(data),data);
        return self.data;
    def strobe(self,reg=0x00):
        """Strobes a strobe register, returning the status."""
        data=[reg];
        self.trans(data);
        return ord(self.data[0]);
    def peek(self,reg,bytes=2):
        """Read a CCSPI Register.  For long regs, result is flipped."""
        data=[reg,0,0];
        
        #Automatically calibrate the len.
        bytes=2;
        
        self.writecmd(self.CCSPIAPP,0x02,len(data),data);
        toret=0;
        #print "Status: %02x" % ord(self.data[0]);
        for i in range(0,bytes):
            toret=toret|(ord(self.data[i+1])<<(8*i));
        return toret;
    def poke(self,reg,val,bytes=-1):
        """Write a CCSPI Register."""
        data=[reg];
        
        #Automatically calibrate the len.
        if bytes==-1:
            bytes=1;
            if reg==0x0a or reg==0x0b or reg==0x10: bytes=5;
        
        for i in range(0,bytes):
            data=data+[(val>>(8*i))&0xFF];
        self.writecmd(self.CCSPIAPP,0x03,len(data),data);
        if self.peek(reg,bytes)!=val and reg!=0x07:
            print "Warning, failed to set r%02x=%02x, got %02x." %(reg,
                                                                   val,
                                                                   self.peek(reg,bytes));
        return;
    
    def status(self):
        """Read the status byte."""
        status=self.strobe(0x00);
        print "Status=%02x" % status;
    
    #Radio stuff begins here.
    def RF_setenc(self,code="GFSK"):
        """Set the encoding type."""
        if code!=GFSK:
            return "%s not supported by the CCSPI24L01.  Try GFSK."
        return;
    def RF_getenc(self):
        """Get the encoding type."""
        return "GFSK";
    def RF_getrate(self):
        rate=self.peek(0x06)&0x28;
        if rate==0x28:
            rate=250*10**3; #256kbps
        elif rate==0x08:
            rate=2*10**6;  #2Mbps
        elif rate==0x00: 
            rate=1*10**6;  #1Mbps
        return rate;
    def RF_setrate(self,rate=2*10**6):
        r6=self.peek(0x06); #RF_SETUP register
        r6=r6&(~0x28);   #Clear rate fields.
        if rate==2*10**6:
            r6=r6|0x08;
        elif rate==1*10**6:
            r6=r6;
        elif rate==250*10**3:
            r6=r6|0x20;
        print "Setting r6=%02x." % r6;
        self.poke(0x06,r6); #Write new setting.
    def RF_setfreq(self,frequency):
        """Set the frequency in Hz."""
        
        print "TODO write the setfreq() function.";
    def RF_getfreq(self):
        """Get the frequency in Hz."""
        print "TODO write the getfreq() function.";
        return 0;
    def RF_getsmac(self):
        """Return the source MAC address."""
        
        return 0xdeadbeef;
    def RF_setsmac(self,mac):
        """Set the source MAC address."""
        return 0xdeadbeef;
    def RF_gettmac(self):
        """Return the target MAC address."""
        return 0xdeadbeef;
    def RF_settmac(self,mac):
        """Set the target MAC address."""
        return 0xdeadbeef;

    def RF_rxpacket(self):
        """Get a packet from the radio.  Returns None if none is waiting."""
        print "Don't know how to get a packet.";
        return None;
    def RF_carrier(self):
        """Hold a carrier wave on the present frequency."""
        print "Don't know how to hold a carrier.";
    packetlen=16;
    def RF_setpacketlen(self,len=16):
        """Set the number of bytes in the expected payload."""
        #self.poke(0x11,len);
        self.packetlen=len;
    def RF_getpacketlen(self):
        """Set the number of bytes in the expected payload."""
        #len=self.peek(0x11);
        self.packetlen=len;
        return len;
    maclen=5;
    def RF_getmaclen(self):
        """Get the number of bytes in the MAC address."""
        choices=[0, 3, 4, 5];
        choice=self.peek(0x03)&3;
        self.maclen=choices[choice];
        return self.maclen;
    def RF_setmaclen(self,len):
        """Set the number of bytes in the MAC address."""
        choices=["illegal", "illegal", "illegal", 
                 1, 2, 3];
        choice=choices[len];
        self.poke(0x03,choice);
        self.maclen=len;
