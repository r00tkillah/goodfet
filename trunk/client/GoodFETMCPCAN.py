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
    """This class uses the regular SPI app to implement a CAN Bus
    adapter on the Goodthopter10 hardware."""
    MCPMODES=["Normal","Sleep","Loopback","Listen-only","Configuration",
              "UNKNOWN","UNKNOWN","PowerUp"];
    def MCPsetup(self):
        """Sets up the ports."""
        self.SPIsetup();
        self.MCPreset(); #Reset the chip.
        
        # We're going to set some registers, so we must be in config
        # mode.
        self.MCPreqstatConfiguration();
        
        # If we don't enable promiscous mode, we'll miss a lot of
        # packets.  It can be manually disabled later.
        #self.poke8(0x60,0xFF); #TODO Does this have any unpleasant side effects?
        self.poke8(0x60,0x66); #Wanted FF, but some bits are reserved.
        
        #Set the default rate.
        self.MCPsetrate();
    
    #Array of supported rates.
    MCPrates=[83.3, 100, 125,
              250, 500, 1000];
    
    def MCPsetrate(self,rate=125):
        """Sets the data rate in kHz."""
        # Now we need to set the timing registers.  See chapter 5 of
        # the MCP2515 datasheet to get some clue as to how this
        # arithmetic of this works, as my comments here will likely be
        # rambling, incoherent, and unchanged after I get the infernal
        # thing working.
        
        # First, we must chose a Time Quanta (QT) which is used to
        # define the durations of these segments.  Section 5.3
        # suggests setting BRP<5:0> to 0x04 to get a TQ=500ns, as a 20
        # MHz crystal gives a clock period of 50ns.  This way, for 125
        # kHz communication, the bit time must be 16 TQ.
        
        # A bit consists of four parts:
        # 1: SyncSeg             1 TQ
        # 2: PropSeg             2 TQ
        # 3: PhaseSeg1 (PS1)     7 TQ
        # 4: PhaseSeg2 (PS2)     6 TQ
        
        # CNF1 with a prescaler of 4 and a SJW of 1 TQ.  SJW of 4
        # might be more stable.
        #self.poke8(0x2a,0x04);
        
        # CNF2 with a BLTMODE of 1, SAM of 0, PS1 of 7TQ, and PRSEG of 2TQ
        #self.poke8(0x29,
        #           0x80   |  # BTLMODE=1
        #           (6<<3) |  # 6+1=7TQ for PHSEG1
        #           (1)       # 1+1=2TQ for PRSEG
        #           );
        
        #CNF3 with a PS2 length of 6TQ.
        #self.poke8(0x28,
        #           5      #5+1=6TQ
        #           );
        
        
        print "Setting rate of %i kHz." % rate;
        
        #These are the new examples.
        if rate==125:
            #125 kHz, 16 TQ, not quite as worked out above.
            CNF1=0x04;
            CNF2=0xB8;
            CNF3=0x05;
        elif rate==100:
            #100 kHz, 20 TQ
            CNF1=0x04;
            CNF2=0xBA;
            CNF3=0x07;
        elif rate>83 and rate<83.5:
            #83+1/3 kHz, 8 TQ
            # 0.04% error from 83.30
            CNF1=0x0E;
            CNF2=0x90;
            CNF3=0x02;
        elif rate==250:
            #256 kHz, 20 TQ
            CNF1=0x01;
            CNF2=0xBA;
            CNF3=0x07;
        elif rate==500:
            #500 kHz, 20 TQ
            CNF1=0x00;
            CNF2=0xBA;
            CNF3=0x07;
        elif rate==1000:
            #1,000 kHz, 10 TQ
            CNF1=0x00;
            CNF2=0xA0;
            CNF3=0x02;
            print "WARNING: Because of chip errata, this probably won't work."
        else:
            print "Given unsupported rate of %i kHz." % rate;
            print "Defaulting to 125kHz.";
            CNF1=0x04;
            CNF2=0xB8;
            CNF3=0x05;
        self.poke8(0x2a,CNF1);
        self.poke8(0x29,CNF2);
        self.poke8(0x28,CNF3);
        
    def MCPreset(self):
        """Reset the MCP2515 chip."""
        self.SPItrans([0xC0]);
    def MCPcanstat(self):
        """Get the CAN Status."""
        return self.peek8(0x0E);
    def MCPreqstatNormal(self):
        """Set the CAN state."""
        state=0x0;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    def MCPreqstatSleep(self):
        """Set the CAN state."""
        state=0x1;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    def MCPreqstatLoopback(self):
        """Set the CAN state."""
        state=0x2;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    def MCPreqstatListenOnly(self):
        """Set the CAN state."""
        state=0x3;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    def MCPreqstatConfiguration(self):
        """Set the CAN state."""
        state=0x4;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    
    def MCPcanstatstr(self):
        """Read the present status as a string."""
        status=self.MCPcanstat();
        opmod=(status&0xE0)>>5;
        return self.MCPMODES[opmod];
    def MCPrxstatus(self):
        """Reads the RX Status by the SPI verb of the same name."""
        data=self.SPItrans([0xB0,0x00]);
        return ord(data[1]);

    def MCPreadstatus(self):
        """Reads the Read Status by the SPI verb of the same name."""
        #See page 67 of the datasheet for the flag names.
        data=self.SPItrans([0xA0,0x00]);
        return ord(data[1]);

    def MCPrts(self,TXB0=False,TXB1=False,TXB2=False):
        """Requests to send one of the transmit buffers."""
        flags=0;
        if TXB0: flags=flags|1;
        if TXB1: flags=flags|2;
        if TXB2: flags=flags|4;
        
        if flags==0:
            print "Warning: Requesting to send no buffer.";
        
        self.SPItrans([0x80|flags]);
    def readrxbuffer(self,packbuf=0):
        """Reads the RX buffer.  Might have old data."""
        data=self.SPItrans([0x90|(packbuf<<2),
                       0x00,0x00, #SID
                       0x00,0x00, #EID
                       0x00,      #DLC
                       0x00, 0x00, 0x00, 0x00,
                       0x00, 0x00, 0x00, 0x00
                       ]);
        return data[1:len(data)];
    def writetxbuffer(self,packet,packbuf=0):
        """Writes the transmit buffer."""
        self.SPItrans([0x40|(packbuf<<1)]+packet);
        
    def rxpacket(self):
        """Reads the next incoming packet from either buffer.
        Returns None immediately if no packet is waiting."""
        status=self.MCPrxstatus()&0xC0;
        if status&0x40:
            #Buffer 0 has higher priority.
            return self.readrxbuffer(0);
        elif status&0x80:
            #Buffer 1 has lower priority.
            return self.readrxbuffer(1);
        else:
            return None;
    def txpacket(self,packet):
        """Transmits a packet through one of the outbound buffers.
        As usual, the packet should begin with SIDH.
        For now, only TXB0 is supported."""
        self.writetxbuffer(packet,0);
        self.MCPrts(TXB0=True);
    def packet2str(self,packet):
        """Converts a packet from the internal format to a string."""
        toprint="";
        for bar in packet:
            toprint=toprint+("%02x "%ord(bar))
        return toprint;
    def peek8(self,adr):
        """Read a byte from the given address.  Untested."""
        data=self.SPItrans([0x03,adr&0xFF,00]);
        return ord(data[2]);
    def MCPbitmodify(self,adr,mask,data):
        """Writes a byte with a mask.  Doesn't work for many registers."""
        data=self.SPItrans([0x05,adr&0xFF,mask&0xFF,data&0xFF]);
        return ord(data[2]);
    def poke8(self,adr,val):
        """Poke a value into RAM.  Untested"""
        self.SPItrans([0x02,adr&0xFF,val&0xFF]);
        newval=self.peek8(adr);
        if newval!=val:
            print "Failed to poke %02x to %02x.  Got %02x." % (adr,val,newval);
            print "Are you not in idle mode?";
        return val;
