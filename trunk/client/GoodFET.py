#!/usr/bin/env python
# GoodFET Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, time, string, cStringIO, struct, glob, serial, os;


class GoodFET:
    """GoodFET Client Library"""
    
    GLITCHAPP=0x71;
    
    def __init__(self, *args, **kargs):
        self.data=[0];
    def timeout(self):
        print "timeout\n";
    def serInit(self, port=None):
        """Open the serial port"""
        
        if port is None and os.environ.get("GOODFET")!=None:
            glob_list = glob.glob(os.environ.get("GOODFET"));
            if len(glob_list) > 0:
                port = glob_list[0];
        if port is None:
            glob_list = glob.glob("/dev/tty.usbserial*");
            if len(glob_list) > 0:
                port = glob_list[0];
        if port is None:
            glob_list = glob.glob("/dev/ttyUSB*");
            if len(glob_list) > 0:
                port = glob_list[0];
        
        self.serialport = serial.Serial(
            port,
            #9600,
            115200,
            parity = serial.PARITY_NONE
            )
        
        #This might cause problems, but it makes failure graceful.
        #self.serialport._timeout = 5;
        
        #Explicitly set RTS and DTR to halt board.
        self.serialport.setRTS(1);
        self.serialport.setDTR(1);
        #Drop DTR, which is !RST, low to begin the app.
        self.serialport.setDTR(0);
        self.serialport.flushInput()
        self.serialport.flushOutput()
        
        #Read and handle the initial command.
        #time.sleep(1);
        self.readcmd(); #Read the first command.
        if(self.verb!=0x7F):
            print "Verb %02x is wrong.  Incorrect firmware?" % self.verb;
        #print "Connected."
    def getbuffer(self,size=0x1c00):
        writecmd(0,0xC2,[size&0xFF,(size>>16)&0xFF]);
        print "Got %02x%02x buffer size." % (self.data[1],self.data[0]);
    def writecmd(self, app, verb, count=0, data=[]):
        """Write a command and some data to the GoodFET."""
        self.serialport.write(chr(app));
        self.serialport.write(chr(verb));
        
        #if data!=None:
        #    count=len(data); #Initial count ignored.
        
        #print "TX %02x %02x" % (app,verb);
        
        #little endian 16-bit length
        self.serialport.write(chr(count&0xFF));
        self.serialport.write(chr(count>>8));
        
        #print "count=%02x, len(data)=%04x" % (count,len(data));
        
        if count!=0:
            for i in range(0,count):
                #print "Converting %02x at %i" % (data[i],i)
                data[i]=chr(data[i]);
            outstr=''.join(data);
            #outstr=data;
            self.serialport.write(outstr);
        if not self.besilent:
            self.readcmd();
        
    besilent=0;
    app=0;
    verb=0;
    count=0;
    data="";

    def readcmd(self):
        """Read a reply from the GoodFET."""
        while 1:
            #print "Reading...";
            self.app=ord(self.serialport.read(1));
            #print "APP=%2x" % self.app;
            self.verb=ord(self.serialport.read(1));
            #print "VERB=%02x" % self.verb;
            self.count=(
                ord(self.serialport.read(1))
                +(ord(self.serialport.read(1))<<8)
                );
            
            #Debugging string; print, but wait.
            if self.app==0xFF and self.verb==0xFF:
                print "# DEBUG %s" % self.serialport.read(self.count);
            else:
                self.data=self.serialport.read(self.count);
                return self.data;
    #Glitching stuff.
    def glitchAPP(self,app):
        """Glitch into a device by its application."""
        self.data=[app&0xff];
        self.writecmd(self.GLITCHAPP,0x80,1,self.data);
        #return ord(self.data[0]);
    def glitchVERB(self,app,verb, data):
        """Glitch during a transaction.."""
        self.data=[app&0xff, verb&0xFF]+data;
        self.writecmd(self.GLITCHAPP,0x81,len(self.data),self.data);
        #return ord(self.data[0]);
    def glitchVoltages(self,low=0x0880, high=0x0fff):
        """Set glitching voltages. (0x0fff is max.)"""
        self.data=[low&0xff, (low>>8)&0xff,
                   high&0xff, (high>>8)&0xff];
        self.writecmd(self.GLITCHAPP,0x90,4,self.data);
        #return ord(self.data[0]);
    def glitchRate(self,count=0x0800):
        """Set glitching count period."""
        self.data=[count&0xff, (count>>8)&0xff];
        self.writecmd(self.GLITCHAPP,0x91,2,
                      self.data);
        #return ord(self.data[0]);
    
    
    #Monitor stuff
    def silent(self,s=0):
        """Transmissions halted when 1."""
        self.besilent=s;
        print "besilent is %i" % self.besilent;
        self.writecmd(0,0xB0,1,[s]);
        
    def out(self,byte):
        """Write a byte to P5OUT."""
        self.writecmd(0,0xA1,1,[byte]);
    def dir(self,byte):
        """Write a byte to P5DIR."""
        self.writecmd(0,0xA0,1,[byte]);
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
    def dumpmem(self,begin,end):
        i=begin;
        while i<end:
            print "%04x %04x" % (i, self.peekword(i));
            i+=2;
    def monitor_ram_pattern(self):
        """Overwrite all of RAM with 0xBEEF."""
        self.writecmd(0,0x90,0,self.data);
        return;
    def monitor_ram_depth(self):
        """Determine how many bytes of RAM are unused by looking for 0xBEEF.."""
        self.writecmd(0,0x91,0,self.data);
        return ord(self.data[0])+(ord(self.data[1])<<8);
    
    #Baud rates.
    baudrates=[115200, 
               9600,
               19200,
               38400,
               57600,
               115200];
    def setBaud(self,baud):
        """Change the baud rate.  TODO fix this."""
        rates=self.baudrates;
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
    def readbyte(self):
        return ord(self.serialport.read(1));
    def findbaud(self):
        for r in self.baudrates:
            print "\nTrying %i" % r;
            self.serialport.setBaudrate(r);
            #time.sleep(1);
            self.serialport.flushInput()
            self.serialport.flushOutput()
            
            for i in range(1,10):
                self.readbyte();
            
            print "Read %02x %02x %02x %02x" % (
                self.readbyte(),self.readbyte(),self.readbyte(),self.readbyte());
    def monitortest(self):
        """Self-test several functions through the monitor."""
        print "Performing monitor self-test.";
        
        if self.peekword(0x0c00)!=0x0c04 and self.peekword(0x0c00)!=0x0c06:
            print "ERROR Fetched wrong value from 0x0c04.";
        self.pokebyte(0x0021,0); #Drop LED
        if self.peekbyte(0x0021)!=0:
            print "ERROR, P1OUT not cleared.";
        self.pokebyte(0x0021,1); #Light LED
        
        print "Self-test complete.";
    
    

    def I2Csetup(self):
        """Move the FET into the I2C application."""
        self.writecmd(0x02,0x10,0,self.data); #SPI/SETUP
    def I2Cstart(self):
        """Start an I2C transaction."""
        self.writecmd(0x02,0x20,0,self.data); #SPI/SETUP
    def I2Cstop(self):
        """Stop an I2C transaction."""
        self.writecmd(0x02,0x21,0,self.data); #SPI/SETUP
    def I2Cread(self,len=1):
        """Read len bytes by I2C."""
        self.writecmd(0x02,0x00,1,[len]); #SPI/SETUP
        return self.data;
    def I2Cwrite(self,bytes):
        """Write bytes by I2C."""
        self.writecmd(0x02,0x01,len(bytes),bytes); #SPI/SETUP
        return ord(self.data[0]);
