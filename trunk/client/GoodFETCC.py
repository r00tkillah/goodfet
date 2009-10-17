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
    """A GoodFET variant for use with Chipcon 8051 Zigbeema SoC."""
    def CChaltcpu(self):
        """Halt the CPU."""
        self.writecmd(0x30,0x86,0,self.data);
    def CCreleasecpu(self):
        """Resume the CPU."""
        self.writecmd(0x30,0x87,0,self.data);
    def CCtest(self):
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
        
        
        #print "Status: %s." % self.CCstatusstr();
        #Exit debugger
        self.CCstop();
        print "Done.";

    def CCsetup(self):
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
    
    CCversions={0x0100:"CC1110",
                0x8500:"CC2430",
                0x8900:"CC2431",
                0x8100:"CC2510",
                0x9100:"CC2511",
                0xFF00:"CCmissing"};
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
    def CCgetPC(self):
        """Get a chipcon's PC."""
        self.writecmd(0x30,0x83,0,None);
        hi=ord(self.data[0]);
        lo=ord(self.data[1]);
        return (hi<<8)+lo;
    def CCdebuginstr(self,instr):
        self.writecmd(0x30,0x88,len(instr),instr);
        return ord(self.data[0]);
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
    def CCpokedatabyte(self,adr,val):
        """Write a byte to data memory."""
        self.data=[adr&0xff, (adr&0xff00)>>8, val];
        self.writecmd(0x30, 0x92, 3, self.data);
        return ord(self.data[0]);
    def CCchiperase(self):
        """Erase all of the target's memory."""
        self.writecmd(0x30,0x80,0,None);
    def CCstatus(self):
        """Check the status."""
        self.writecmd(0x30,0x84,0,None);
        return ord(self.data[0])
    CCstatusbits={0x80 : "erased",
                  0x40 : "pcon_idle",
                  0x20 : "halted",
                  0x10 : "pm0",
                  0x08 : "halted",
                  0x04 : "locked",
                  0x02 : "oscstable",
                  0x01 : "overflow"};
    def CCstatusstr(self):
        """Check the status as a string."""
        status=self.CCstatus();
        str="";
        i=1;
        while i<0x100:
            if(status&i):
                str="%s %s" %(self.CCstatusbits[i],str);
            i*=2;
        return str;
    def CCstart(self):
        """Start debugging."""
        self.writecmd(0x30,0x20,0,self.data);
        ident=self.CCidentstr();
        print "Target identifies as %s." % ident;
        #print "Status: %s." % self.CCstatusstr();
        self.CCreleasecpu();
        self.CChaltcpu();
        #print "Status: %s." % self.CCstatusstr();
        
    def CCstop(self):
        """Stop debugging."""
        self.writecmd(0x30,0x21,0,self.data);
    def CCstep_instr(self):
        """Step one instruction."""
        self.writecmd(0x30,0x89,0,self.data);

