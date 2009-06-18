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
        print "inited\n";
        self.data=[0];
    def timeout(self):
        print "timout\n";
    def serInit(self, port):
        """Open the serial port"""
        self.serialport = serial.Serial(
            port,
            9600,
            parity = serial.PARITY_NONE
            )
        #Drop DTR, which is !RST, low to begin the app.
        self.serialport.setDTR(0);
        self.serialport.flushInput()
        self.serialport.flushOutput()
        
        #Read and handle the initial command.
        time.sleep(1);
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
        print "Initializing SPI.";
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
    def MSP430test(self):
        """Test MSP430 JTAG.  Requires that a chip be attached."""
        self.MSP430setup();
        self.MSP430start();
        self.MSP430haltcpu();
        
        ident=self.MSP430peek(0x0ff0);
        print "Target identifies as %04x." % ident;
        if ident==0xffff:
            print "Is anything connected?";
        print "Testing RAM.";
        temp=self.MSP430peek(0x0200);
        self.MSP430poke(0x0200,0xdead);
        if(self.MSP430peek(0x0200)!=0xdead):
            print "Poke of 0x0200 did not set to 0xDEAD properly.";
            exit;
        self.MSP430poke(0x0200,temp); #restore old value.
        self.MSP430releasecpu();
        
    def MSP430dumpbsl(self):
        i=0xC00;
        while i<0x1000:
            print "%04x %04x" % (i, self.MSP430peek(i));
            i+=2;

