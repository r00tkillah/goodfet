#!/usr/bin/env python
# GoodFET Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# Presently being rewritten.

import sys, time, string, cStringIO, struct, glob, serial, os;

from GoodFET import GoodFET;

class GoodFETMSP430(GoodFET):
    MSP430APP=0x11;  #Changed by inheritors.
    CoreID=0;
    DeviceID=0;
    JTAGID=0;
    MSP430ident=0;
    def MSP430setup(self):
        """Move the FET into the MSP430 JTAG application."""
        self.writecmd(self.MSP430APP,0x10,0,None);
        
    def MSP430stop(self):
        """Stop debugging."""
        self.writecmd(self.MSP430APP,0x21,0,self.data);
    
    def MSP430coreid(self):
        """Get the Core ID."""
        self.writecmd(self.MSP430APP,0xF0);
        CoreID=ord(self.data[0])+(ord(self.data[1])<<8);
        return CoreID;
    def MSP430deviceid(self):
        """Get the Core ID."""
        self.writecmd(self.MSP430APP,0xF1);
        DeviceID=(
            ord(self.data[0])+(ord(self.data[1])<<8)+
            (ord(self.data[2])<<16)+(ord(self.data[3])<<24));
        return DeviceID;
    def MSP430peek(self,adr):
        """Read a word at an address."""
        self.data=[adr&0xff, (adr&0xff00)>>8,
                   (adr&0xff0000)>>16,(adr&0xff000000)>>24,
                   ]; 
        self.writecmd(self.MSP430APP,0x02,4,self.data,1);
        return ord(self.data[0])+(ord(self.data[1])<<8);
    def MSP430peekblock(self,adr,blocks=1):
        """Grab a few block from an SPI Flash ROM.  Block size is unknown"""
        data=[adr&0xff, (adr&0xff00)>>8,
                   (adr&0xff0000)>>16,(adr&0xff000000)>>24,
                   blocks];
        
        self.writecmd(self.MSP430APP,0x02,5,data,blocks);
        return self.data;
    
    def MSP430poke(self,adr,val):
        """Write the contents of memory at an address."""
        self.data=[adr&0xff, (adr&0xff00)>>8,
                   (adr&0xff0000)>>16,(adr&0xff000000)>>24,
                   val&0xff, (val&0xff00)>>8];
        self.writecmd(self.MSP430APP,0x03,6,self.data);
        return ord(self.data[0])+(ord(self.data[1])<<8);
    def MSP430start(self):
        """Start debugging."""
        self.writecmd(self.MSP430APP,0x20,0,self.data);
        self.JTAGID=ord(self.data[0]);
        #print "Identified as %02x." % self.JTAGID;
        if(not (self.JTAGID==0x89 or self.JTAGID==0x91)):
            print "Error, misidentified as %02x." % self.JTAGID;
        
    def MSP430haltcpu(self):
        """Halt the CPU."""
        self.writecmd(self.MSP430APP,0xA0,0,self.data);
    def MSP430releasecpu(self):
        """Resume the CPU."""
        self.writecmd(self.MSP430APP,0xA1,0,self.data);
    def MSP430shiftir8(self,ins):
        """Shift the 8-bit Instruction Register."""
        data=[ins];
        self.writecmd(self.MSP430APP,0x80,1,data);
        return ord(self.data[0]);
    def MSP430shiftdr16(self,dat):
        """Shift the 16-bit Data Register."""
        data=[dat&0xFF,(dat&0xFF00)>>8];
        self.writecmd(self.MSP430APP,0x81,2,data);
        return ord(self.data[0])#+(ord(self.data[1])<<8);
    def MSP430setinstrfetch(self):
        """Set the instruction fetch mode."""
        self.writecmd(self.MSP430APP,0xC1,0,self.data);
        return self.data[0];
    def MSP430ident(self):
        """Grab self-identification word from 0x0FF0 as big endian."""
        ident=0x00;
        if(self.JTAGID==0x89):
            i=self.MSP430peek(0x0ff0);
            ident=((i&0xFF00)>>8)+((i&0xFF)<<8)
            
        if(self.JTAGID==0x91):
            i=self.MSP430peek(0x1A04);
            ident=((i&0xFF00)>>8)+((i&0xFF)<<8)
            #ident=0x0091;
        
        return ident;
    def MSP430identstr(self):
        """Grab model string."""
        return self.MSP430devices.get(self.MSP430ident());
    MSP430devices={
        #MSP430F2xx
        0xf227: "MSP430F22xx",
        0xf213: "MSP430F21x1",
        0xf249: "MSP430F24x",
        0xf26f: "MSP430F261x",
        
        #MSP430F1xx
        0xf16c: "MSP430F161x",
        0xf149: "MSP430F13x", #or f14x(1)
        0xf112: "MSP430F11x", #or f11x1
        0xf143: "MSP430F14x",
        0xf112: "MSP430F11x", #or F11x1A
        0xf123: "MSP430F1xx", #or F123x
        0x1132: "MSP430F1122", #or F1132
        0x1232: "MSP430F1222", #or F1232
        0xf169: "MSP430F16x",
        
        #MSP430F4xx
        0xF449: "MSP430F43x", #or F44x
        0xF427: "MSP430FE42x", #or FW42x, F415, F417
        0xF439: "MSP430FG43x",
        0xf46f: "MSP430FG46xx", #or F471xx
        
        }
    def MSP430test(self):
        """Test MSP430 JTAG.  Requires that a chip be attached."""
        if self.MSP430ident()==0xffff:
            print "Is anything connected?";
        print "Testing RAM from 1c00 to 1d00.";
        for a in range(0x1c00,0x1d00):
            self.MSP430poke(a,0);
            if(self.MSP430peek(a)!=0):
                print "Fault at %06x" % a;
            self.MSP430poke(a,0xffff);
            if(self.MSP430peek(a)!=0xffff):
                print "Fault at %06x" % a;
        print "RAM Test Complete."
        for a in range(1,5):
            print "Identity %04x" % self.MSP430ident();
            
    def MSP430flashtest(self):
        self.MSP430masserase();
        i=0x2500;
        while(i<0xFFFF):
            if(self.MSP430peek(i)!=0xFFFF):
                print "ERROR: Unerased flash at %04x."%i;
            self.MSP430writeflash(i,0xDEAD);
            i+=2;
    def MSP430masserase(self):
        """Erase MSP430 flash memory."""
        self.writecmd(self.MSP430APP,0xE3,0,None);
    def MSP430writeflash(self,adr,val):
        """Write a word of flash memory."""
        if(self.MSP430peek(adr)!=0xFFFF):
            print "FLASH ERROR: %04x not clear." % adr;
        data=[adr&0xFF,(adr&0xFF00)>>8,val&0xFF,(val&0xFF00)>>8];
        self.writecmd(self.MSP430APP,0xE1,4,data);
        rval=ord(self.data[0])+(ord(self.data[1])<<8);
        if(val!=rval):
            print "FLASH WRITE ERROR AT %04x.  Found %04x, wrote %04x." % (adr,rval,val);
        
    def MSP430dumpbsl(self):
        self.MSP430dumpmem(0xC00,0xfff);
    def MSP430dumpallmem(self):
        self.MSP430dumpmem(0x200,0xffff);
    def MSP430dumpmem(self,begin,end):
        i=begin;
        while i<end:
            print "%04x %04x" % (i, self.MSP430peek(i));
            i+=2;
