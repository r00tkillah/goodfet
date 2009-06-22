#!/usr/bin/env python
# GoodFET Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is ugly as sin, for bootstrapping the firmware only.
# Rewrite cleanly as soon as is convenient.

import sys, time, string, cStringIO, struct
sys.path.append("/usr/lib/tinyos")
import serial


class GoodFET:
    def __init__(self, *args, **kargs):
        self.data=[0];
    def timeout(self):
        print "timout\n";
    def serInit(self, port):
        """Open the serial port"""
        self.serialport = serial.Serial(
            port,
            #9600,
            115200,
            parity = serial.PARITY_NONE
            )
        #Drop DTR, which is !RST, low to begin the app.
        self.serialport.setDTR(0);
        self.serialport.flushInput()
        self.serialport.flushOutput()
        
        #Read and handle the initial command.
        #time.sleep(1);
        self.readcmd(); #Read the first command.
        if(self.verb!=0x7F):
            print "Verb is wrong.  Incorrect firmware?";
        
    def writecmd(self, app, verb, count, data):
        """Write a command and some data to the GoodFET."""
        self.serialport.write(chr(app));
        self.serialport.write(chr(verb));
        self.serialport.write(chr(count));
        #print "count=%02x, len(data)=%04x" % (count,len(data));
        if count!=0:
            for d in data:
                self.serialport.write(chr(d));
        self.readcmd();  #Uncomment this later, to ensure a response.
    def readcmd(self):
        """Read a reply from the GoodFET."""
        self.app=ord(self.serialport.read(1));
        self.verb=ord(self.serialport.read(1));
        self.count=ord(self.serialport.read(1));
        if self.count>0:
            self.data=self.serialport.read(self.count);
        #print "READ %02x %02x %02x " % (self.app, self.verb, self.count);
        
    #Monitor stuff
    def peekbyte(self,address):
        """Read a byte of memory from the monitor."""
        self.data=[address&0xff,address>>8];
        self.writecmd(0,0x02,2,self.data);
        #self.readcmd();
        return ord(self.data[0]);
    def peekword(self,address):
        """Read a word of memory from the monitor."""
        return self.peekbyte(address)+(self.peekbyte(address+1)<<8);
    def pokebyte(self,address,value):
        """Set a byte of memory by the monitor."""
        self.data=[address&0xff,address>>8,value];
        self.writecmd(0,0x03,3,self.data);
        return ord(self.data[0]);
    def setBaud(self,baud):
        rates=[9600, 9600, 19200, 38400];
        self.data=[baud];
        print "Changing FET baud."
        self.serialport.write(chr(0x00));
        self.serialport.write(chr(0x80));
        self.serialport.write(chr(1));
        self.serialport.write(chr(baud));
        
        print "Changed host baud."
        self.serialport.setBaudrate(rates[baud]);
        time.sleep(1);
        self.serialport.flushInput()
        self.serialport.flushOutput()
        
        print "Baud is now %i." % rates[baud];
        return;
    def monitortest(self):
        """Self-test several functions through the monitor."""
        print "Performing monitor self-test.";
        
        if self.peekword(0x0c00)!=0x0c04:
            print "ERROR Fetched wrong value from 0x0c04.";
        self.pokebyte(0x0021,0); #Drop LED
        if self.peekbyte(0x0021)!=0:
            print "ERROR, P1OUT not cleared.";
        self.pokebyte(0x0021,1); #Light LED
        
        print "Self-test complete.";
    
    def spisetup(self):
        """Moved the FET into the SPI application."""
        self.writecmd(1,0x10,0,self.data); #SPI/SETUP
        #self.readcmd();
    def spitrans8(self,byte):
        """Read and write 8 bits by SPI."""
        self.data=[byte];
        self.writecmd(1,0,1,self.data);    #SPI exchange
        #self.readcmd();
        
        if self.app!=1 or self.verb!=0:
            print "Error in SPI transaction; app=%02x, verb=%02x" % (self.app, self.verb);
        return ord(self.data[0]);
    def MSP430setup(self):
        """Move the FET into the MSP430 JTAG application."""
        print "Initializing MSP430.";
        self.writecmd(0x11,0x10,0,self.data);
    def CCsetup(self):
        """Move the FET into the CC2430/CC2530 application."""
        print "Initializing Chipcon.";
        self.writecmd(0x30,0x10,0,self.data);
    def CCrd_config(self):
        """Read the config register of a Chipcon."""
        self.writecmd(0x30,0x82,0,self.data);
        return ord(self.data[0]);
    def CCwr_config(self,config):
        """Write the config register of a Chipcon."""
        self.writecmd(0x30,0x81,1,[config&0xFF]);
    def CCident(self):
        """Get a chipcon's ID."""
        self.writecmd(0x30,0x8B,0,None);
        chip=ord(self.data[0]);
        rev=ord(self.data[1]);
        return (chip<<8)+rev;
    def MSP430peek(self,adr):
        """Read the contents of memory at an address."""
        self.data=[adr&0xff, (adr&0xff00)>>8];
        self.writecmd(0x11,0x02,2,self.data);
        return ord(self.data[0])+(ord(self.data[1])<<8);
    def MSP430poke(self,adr,val):
        """Read the contents of memory at an address."""
        self.data=[adr&0xff, (adr&0xff00)>>8, val&0xff, (val&0xff00)>>8];
        self.writecmd(0x11,0x03,4,self.data);
        return;# ord(self.data[0])+(ord(self.data[1])<<8);
    
    def MSP430start(self):
        """Start debugging."""
        self.writecmd(0x11,0x20,0,self.data);
        ident=self.MSP430ident();
        print "Target identifies as %04x." % ident;
    
    def CCstart(self):
        """Start debugging."""
        self.writecmd(0x30,0x20,0,self.data);
        ident=self.CCident();
        print "Target identifies as %04x." % ident;
    def CCstop(self):
        """Stop debugging."""
        self.writecmd(0x30,0x21,0,self.data);
        
    def MSP430stop(self):
        """Stop debugging."""
        self.writecmd(0x11,0x21,0,self.data);
    def MSP430haltcpu(self):
        """Halt the CPU."""
        self.writecmd(0x11,0xA0,0,self.data);
    def MSP430releasecpu(self):
        """Resume the CPU."""
        self.writecmd(0x11,0xA1,0,self.data);

    def MSP430shiftir8(self,ins):
        """Shift the 8-bit Instruction Register."""
        data=[ins];
        self.writecmd(0x11,0x80,1,data);
        return ord(self.data[0]);
    def MSP430shiftdr16(self,dat):
        """Shift the 16-bit Data Register."""
        data=[dat&0xFF,(dat&0xFF00)>>8];
        self.writecmd(0x11,0x81,2,data);
        return ord(self.data[0])#+(ord(self.data[1])<<8);
    def MSP430setinstrfetch(self):
        """Set the instruction fetch mode."""
        self.writecmd(0x11,0xC1,0,self.data);
        return self.data[0];
    def MSP430ident(self):
        """Grab self-identification word from 0x0FF0 as big endian."""
        i=self.MSP430peek(0x0ff0);
        return ((i&0xFF00)>>8)+((i&0xFF)<<8)
    def MSP430test(self):
        """Test MSP430 JTAG.  Requires that a chip be attached."""
        if self.MSP430ident()==0xffff:
            print "Is anything connected?";
        print "Testing RAM.";
        temp=self.MSP430peek(0x0200);
        self.MSP430poke(0x0200,0xdead);
        if(self.MSP430peek(0x0200)!=0xdead):
            print "Poke of 0x0200 did not set to 0xDEAD properly.";
            return;
        self.MSP430poke(0x0200,temp); #restore old value.
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
        self.writecmd(0x11,0xE3,0,None);
    def MSP430writeflash(self,adr,val):
        """Write a word of flash memory."""
        if(self.MSP430peek(adr)!=0xFFFF):
            print "FLASH ERROR: %04x not clear." % adr;
        data=[adr&0xFF,(adr&0xFF00)>>8,val&0xFF,(val&0xFF00)>>8];
        self.writecmd(0x11,0xE1,4,data);
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

    def CCtest(self):
        self.CCstop();
        print "Done.";
