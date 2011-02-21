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
    CCversions={0x233d: "CC2420",
                }
    def setup(self):
        """Move the FET into the CCSPI application."""
        self.writecmd(self.CCSPIAPP,0x10,0,self.data); #CCSPI/SETUP
        
        #Set up the radio for ZigBee
        self.strobe(0x01);       #SXOSCON
        self.poke(0x11, 0x0AC2); #MDMCTRL0
        self.poke(0x12, 0x0500); #MDMCTRL1
        self.poke(0x1C, 0x007F); #IOCFG0
        self.poke(0x19, 0x01C4); #SECCTRL0, disabling crypto
        
    def ident(self):
        return self.peek(0x1E); #MANFIDL
    def identstr(self):
        manfidl=self.peek(0x1E);
        #manfidh=self.peek(0x1f);
        try:
            return "%s" % (self.CCversions[manfidl]); 
        except:
            return "Unknown0x%04x" % manfidl;
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
    def CC_RFST_IDLE(self):
        """Switch the radio to idle mode, clearing overflows and errors."""
        self.strobe(0x06); #SRXOFF
    def CC_RFST_TX(self):
        """Switch the radio to TX mode."""
        self.strobe(0x04);  #0x05 for CCA
    def CC_RFST_RX(self):
        """Switch the radio to RX mode."""
        self.strobe(0x03);
    def CC_RFST_CAL(self):
        """Calibrate strobe the radio."""
        self.strobe(0x02);
    def CC_RFST(self,state=0x00):
        self.strobe(state);
        return;
    def peek(self,reg,bytes=2):
        """Read a CCSPI Register.  For long regs, result is flipped."""
        
        #Reg is ORed with 0x40 by the GoodFET.
        data=[reg,0,0];
        
        #Automatically calibrate the len.
        bytes=2;
        
        self.writecmd(self.CCSPIAPP,0x02,len(data),data);
        toret=(
            ord(self.data[2])+
            (ord(self.data[1])<<8)
            );
        return toret;
    def poke(self,reg,val,bytes=2):
        """Write a CCSPI Register."""
        data=[reg,(val>>8)&0xFF,val&0xFF];
        self.writecmd(self.CCSPIAPP,0x03,len(data),data);
        if self.peek(reg,bytes)!=val:
            print "Warning, failed to set r%02x=0x%04x, got %02x." %(
                reg,
                val,
                self.peek(reg,bytes));
        return;
    
    def status(self):
        """Read the status byte."""
        status=self.strobe(0x00);
        print "Status=%02x" % status;
    
    #Radio stuff begins here.
    def RF_setenc(self,code="802.15.4"):
        """Set the encoding type."""
        return;
    def RF_getenc(self):
        """Get the encoding type."""
        return "802.15.4";
    def RF_getrate(self):
        return 0;
    def RF_setrate(self,rate=0):
        return 0;
    def RF_setfreq(self,frequency):
        """Set the frequency in Hz."""
        mhz=frequency/1000000;
        fsctrl=self.peek(0x18)&~0x3FF;
        fsctrl=fsctrl+int(mhz-2048)
        self.poke(0x18,fsctrl);
    def RF_getfreq(self):
        """Get the frequency in Hz."""
        fsctrl=self.peek(0x18);
        mhz=2048+(fsctrl&0x3ff)
        return mhz*1000000;
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
    def RF_getrssi(self):
        """Returns the received signal strenght, with a weird offset."""
        rssival=self.peek(0x13)&0xFF; #raw RSSI register
        return rssival^0x80;
    lastpacket=range(0,0xff);
    def RF_rxpacket(self):
        """Get a packet from the radio.  Returns None if none is waiting.  In
        order to not require the SFD, FIFO, or FIFOP lines, this
        implementation works by comparing the buffer to the older
        contents.
        """
        
        # TODO -- Flush only if there's an overflow.
        self.strobe(0x08); #SFLUSHRX
        
        data="\0";
        self.data=data;
        self.writecmd(self.CCSPIAPP,0x80,len(data),data);
        buffer=self.data;
        
        self.lastpacket=buffer;
        if(len(buffer)==0):
            return None;
        return buffer;
    def RF_rxpacket_old(self):
        """Get a packet from the radio.  Returns None if none is waiting.  In
        order to not require the SFD, FIFO, or FIFOP lines, this
        implementation works by comparing the buffer to the older
        contents.
        """
        self.strobe(0x03); #SRXON
        self.strobe(0x08); #SFLUSHRX
        
        buffer=range(0,0xff);
        buffer[0]=0x3F | 0x40; #RXFIFO
        buffer=self.trans(buffer);
        
        new=False;
        for foo in range(0,ord(buffer[0])):
            if buffer[foo]!=self.lastpacket[foo]:
                new=True;
        if not new:
            return None;
        
        
        self.lastpacket=buffer;
        return buffer;
    def RF_carrier(self):
        """Hold a carrier wave on the present frequency."""
        print "Don't know how to hold a carrier.";
    def RF_promiscuity(self,promiscuous=1):
        mdmctrl0=self.peek(0x11);
        print "mdmctrl0 was %04x" % mdmctrl0;
        mdmctrl0=mdmctrl0&(~0x800);
        print "mdmctrl0 is now %04x" % mdmctrl0;
        self.poke(0x11,mdmctrl0);
        return;
        
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
