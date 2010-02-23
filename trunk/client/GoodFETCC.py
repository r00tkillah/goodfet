#!/usr/bin/env python
# GoodFET Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys;
import binascii;

from GoodFET import GoodFET;
from intelhex import IntelHex;

class GoodFETCC(GoodFET):
    """A GoodFET variant for use with Chipcon 8051 Zigbee SoC."""
    APP=0x30;
    
    def CChaltcpu(self):
        """Halt the CPU."""
        self.writecmd(0x30,0x86,0,self.data);
    def CCreleasecpu(self):
        """Resume the CPU."""
        self.writecmd(0x30,0x87,0,self.data);
    def test(self):
        self.CCreleasecpu();
        self.CChaltcpu();
        #print "Status: %s" % self.CCstatusstr();
        
        #Grab ident three times, should be equal.
        ident1=self.CCident();
        ident2=self.CCident();
        ident3=self.CCident();
        if(ident1!=ident2 or ident2!=ident3):
            print "Error, repeated ident attempts unequal."
            print "%04x, %04x, %04x" % (ident1, ident2, ident3);
        
        #Single step, printing PC.
        print "Tracing execution at startup."
        for i in range(1,15):
            pc=self.CCgetPC();
            byte=self.CCpeekcodebyte(i);
            #print "PC=%04x, %02x" % (pc, byte);
            self.CCstep_instr();
        
        print "Verifying that debugging a NOP doesn't affect the PC."
        for i in range(1,15):
            pc=self.CCgetPC();
            self.CCdebuginstr([0x00]);
            if(pc!=self.CCgetPC()):
                print "ERROR: PC changed during CCdebuginstr([NOP])!";
        
        print "Checking pokes to XRAM."
        for i in range(0xf000,0xf020):
            self.CCpokedatabyte(i,0xde);
            if(self.CCpeekdatabyte(i)!=0xde):
                print "Error in XDATA at 0x%04x" % i;
        
        #print "Status: %s." % self.CCstatusstr();
        #Exit debugger
        self.stop();
        print "Done.";

    def setup(self):
        """Move the FET into the CC2430/CC2530 application."""
        #print "Initializing Chipcon.";
        self.writecmd(0x30,0x10,0,self.data);
    def CCrd_config(self):
        """Read the config register of a Chipcon."""
        self.writecmd(0x30,0x82,0,self.data);
        return ord(self.data[0]);
    def CCwr_config(self,config):
        """Write the config register of a Chipcon."""
        self.writecmd(0x30,0x81,1,[config&0xFF]);
    def CClockchip(self):
        """Set the flash lock bit in info mem."""
        self.writecmd(0x30, 0x9A, 0, None);
    def lock(self):
        """Set the flash lock bit in info mem."""
        self.CClockchip();
    

    CCversions={0x0100:"CC1110",
                0x8500:"CC2430",
                0x8900:"CC2431",
                0x8100:"CC2510",
                0x9100:"CC2511",
                0xA500:"CC2530", #page 52 of SWRU191
                0xB500:"CC2531",
                0xFF00:"CCmissing"};
    CCpagesizes={0x01: 1024, #"CC1110",
                 0x85: 2048, #"CC2430",
                 0x89: 2048, #"CC2431",
                 0x81: 1024, #"CC2510",
                 0x91: 1024, #"CC2511",
                 0xA5: 2048, #"CC2530", #page 52 of SWRU191
                 0xB5: 2048, #"CC2531",
                 0xFF: 0    } #"CCmissing"};
    def infostring(self):
        return self.CCidentstr();
    def CCidentstr(self):
        ident=self.CCident();
        chip=self.CCversions.get(ident&0xFF00);
        return "%s/r%02x" % (chip, ident&0xFF); 
    def CCident(self):
        """Get a chipcon's ID."""
        self.writecmd(0x30,0x8B,0,None);
        chip=ord(self.data[0]);
        rev=ord(self.data[1]);
        return (chip<<8)+rev;
    def CCpagesize(self):
        """Get a chipcon's ID."""
        self.writecmd(0x30,0x8B,0,None);
        chip=ord(self.data[0]);
        size=self.CCpagesizes.get(chip);
        if(size<10):
            print "ERROR: Pagesize undefined.";
            print "chip=%02x" %chip;
            sys.exit(1);
            #return 2048;
        return size;
    def CCgetPC(self):
        """Get a chipcon's PC."""
        self.writecmd(0x30,0x83,0,None);
        hi=ord(self.data[0]);
        lo=ord(self.data[1]);
        return (hi<<8)+lo;
    def CCcmd(self,phrase):
        self.writecmd(0x30,0x00,len(phrase),phrase);
        val=ord(self.data[0]);
        print "Got %02x" % val;
        return val;
    def CCdebuginstr(self,instr):
        self.writecmd(0x30,0x88,len(instr),instr);
        return ord(self.data[0]);
    def peek8(self,address, memory="code"):
        if(memory=="code" or memory=="flash" or memory=="vn"):
            return self.CCpeekcodebyte(address);
        elif(memory=="data" or memory=="xdata" or memory=="ram"):
            return self.CCpeekdatabyte(address);
        elif(memory=="idata" or memory=="iram"):
            return self.CCpeekirambyte(address);
        print "%s is an unknown memory." % memory;
        return 0xdead;
    def CCpeekcodebyte(self,adr):
        """Read the contents of code memory at an address."""
        self.data=[adr&0xff, (adr&0xff00)>>8];
        self.writecmd(0x30,0x90,2,self.data);
        return ord(self.data[0]);
    def CCpeekdatabyte(self,adr):
        """Read the contents of data memory at an address."""
        self.data=[adr&0xff, (adr&0xff00)>>8];
        self.writecmd(0x30,0x91, 2, self.data);
        return ord(self.data[0]);
    def CCpeekirambyte(self,adr):
        """Read the contents of IRAM at an address."""
        self.data=[adr&0xff];
        self.writecmd(0x30,0x02, 1, self.data);
        return ord(self.data[0]);
    def CCpeekiramword(self,adr):
        """Read the little-endian contents of IRAM at an address."""
        return self.CCpeekirambyte(adr)+(
            self.CCpeekirambyte(adr+1)<<8);
    def CCpokeiramword(self,adr,val):
        self.CCpokeirambyte(adr,val&0xff);
        self.CCpokeirambyte(adr+1,(val>>8)&0xff);
    def CCpokeirambyte(self,adr,val):
        """Write the contents of IRAM at an address."""
        self.data=[adr&0xff, val&0xff];
        self.writecmd(0x30,0x02, 2, self.data);
        return ord(self.data[0]);
    
    def CCpokedatabyte(self,adr,val):
        """Write a byte to data memory."""
        self.data=[adr&0xff, (adr&0xff00)>>8, val];
        self.writecmd(0x30, 0x92, 3, self.data);
        return ord(self.data[0]);
    def CCchiperase(self):
        """Erase all of the target's memory."""
        self.writecmd(0x30,0x80,0,None);
    def erase(self):
        """Erase all of the target's memory."""
        self.CCchiperase();
    
    def CCstatus(self):
        """Check the status."""
        self.writecmd(0x30,0x84,0,None);
        return ord(self.data[0])
    #Same as CC2530
    CCstatusbits={0x80 : "erase_busy",
                  0x40 : "pcon_idle",
                  0x20 : "cpu_halted",
                  0x10 : "pm0",
                  0x08 : "halt_status",
                  0x04 : "locked",
                  0x02 : "oscstable",
                  0x01 : "overflow"
                  };
    CCconfigbits={0x20 : "soft_power_mode",   #new for CC2530
                  0x08 : "timers_off",
                  0x04 : "dma_pause",
                  0x02 : "timer_suspend",
                  0x01 : "sel_flash_info_page" #stricken from CC2530
                  };
                  
    def status(self):
        """Check the status as a string."""
        status=self.CCstatus();
        str="";
        i=1;
        while i<0x100:
            if(status&i):
                str="%s %s" %(self.CCstatusbits[i],str);
            i*=2;
        return str;
    def start(self):
        """Start debugging."""
        self.writecmd(0x30,0x20,0,self.data);
        ident=self.CCidentstr();
        #print "Target identifies as %s." % ident;
        #print "Status: %s." % self.status();
        self.CCreleasecpu();
        self.CChaltcpu();
        #print "Status: %s." % self.status();
        
    def stop(self):
        """Stop debugging."""
        self.writecmd(0x30,0x21,0,self.data);
    def CCstep_instr(self):
        """Step one instruction."""
        self.writecmd(0x30,0x89,0,self.data);
    def CCeraseflashbuffer(self):
        """Erase the 2kB flash buffer"""
        self.writecmd(0x30,0x99);
    def CCflashpage(self,adr):
        """Flash 2kB a page of flash from 0xF000 in XDATA"""
        data=[adr&0xFF,
              (adr>>8)&0xFF,
              (adr>>16)&0xFF,
              (adr>>24)&0xFF];
        print "Flashing buffer to 0x%06x" % adr;
        self.writecmd(0x30,0x95,4,data);

    def flash(self,file):
        """Flash an intel hex file to code memory."""
        print "Flashing %s" % file;
        
        h = IntelHex(file);
        page = 0x0000;
        pagelen = self.CCpagesize(); #Varies by chip.
        
        #print "page=%04x, pagelen=%04x" % (page,pagelen);
        
        bcount = 0;
        
        #Wipe the RAM buffer for the next flash page.
        self.CCeraseflashbuffer();
        for i in h._buf.keys():
            while(i>=page+pagelen):
                if bcount>0:
                    self.CCflashpage(page);
                    #client.CCeraseflashbuffer();
                    bcount=0;
                    print "Flashed page at %06x" % page
                page+=pagelen;
                    
            #Place byte into buffer.
            self.CCpokedatabyte(0xF000+i-page,
                                h[i]);
            bcount+=1;
            if(i%0x100==0):
                print "Buffering %04x toward %06x" % (i,page);
        #last page
        self.CCflashpage(page);
        print "Flashed final page at %06x" % page;
                        
