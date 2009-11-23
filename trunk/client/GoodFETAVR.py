#!/usr/bin/env python
# GoodFET SPI and SPIFlash Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, time, string, cStringIO, struct, glob, serial, os;

from GoodFET import GoodFET;

class GoodFETAVR(GoodFET):
    AVRAPP=0x32;
    AVRVendors={0x1E: "Atmel",
                0x00: "Locked",
                };
    
    #List from avr910.asm and other sources.
    #More devices at http://avr.fenceline.de/device_data.html
    AVRDevices={
        0x9003: "tiny10",
        0x9004: "tiny11",
        0x9005: "tiny12",
        0x9006: "tiny15",
        0x9007: "tiny13",
        0x9108: "tiny25",
        0x930B: "tiny85",
        0x9206: "tiny45",
        
        0x9001: "S1200",
        
        0x9101: "S1213",
        0x9102: "S2323",
        0x9105: "S2333",
        0x9103: "S2343",
        
        0x9201: "S4414",
        0x9203: "S4433",
        0x9202: "S4434",
        
        0x9301: "S8515",
        0x9303: "S8535",
        
        0x9305: "mega83",
        0x930a: "mega88",
        0x9701: "mega103",
        0x9401: "mega161",
        0x9402: "mega163",
        0x9406: "mega168",
        
        0x950f: "mega328",
        0x950d: "mega325",
        0x9508: "mega32"
        };
    
    def setup(self):
        """Move the FET into the SPI application."""
        self.writecmd(self.AVRAPP,0x10,0,self.data); #SPI/SETUP
    
    def trans(self,data):
        """Exchange data by AVR.
        Input should probably be 4 bytes."""
        self.data=data;
        self.writecmd(self.AVRAPP,0x00,len(data),data);
        return self.data;

    def start(self):
        """Start the connection."""
        self.writecmd(self.AVRAPP,0x20,0,None);
    def erase(self):
        """Erase the target chip."""
        self.writecmd(self.AVRAPP,0xF0,0,None);
    def lockbits(self):
        """Read the target's lockbits."""
        self.writecmd(self.AVRAPP,0x82,0,None);
        return ord(self.data[0]);
    def eeprompeek(self, adr):
        """Read a byte of the target's EEPROM."""
        self.writecmd(self.AVRAPP,0x81 ,2,
                      [ (adr&0xFF), (adr>>8)]
                      );#little-endian address
        return ord(self.data[0]);
    def flashpeek(self, adr):
        """Read a byte of the target's EEPROM."""
        self.writecmd(self.AVRAPP,0x02 ,2,
                      [ (adr&0xFF), (adr>>8)]
                      );#little-endian address
        return ord(self.data[0]);
    def flashpeekblock(self, adr):
        """Read a byte of the target's EEPROM."""
        self.writecmd(self.AVRAPP,0x02 ,4,
                      [ (adr&0xFF), (adr>>8) &0xFF, 0x80, 0x00]
                      );
        return self.data;
    
    def eeprompoke(self, adr, val):
        """Write a byte of the target's EEPROM."""
        self.writecmd(self.AVRAPP,0x91 ,3,
                      [ (adr&0xFF), (adr>>8), val]
                      );#little-endian address
        return ord(self.data[0]);
    
    def identstr(self):
        """Return an identifying string."""
        self.writecmd(self.AVRAPP,0x83,0, None);
        vendor=self.AVRVendors.get(ord(self.data[0]));
        deviceid=(ord(self.data[1])<<8)+ord(self.data[2]);
        device=self.AVRDevices.get(deviceid);
        
        #Return hex if device is unknown.
        #They are similar enough that it needn't be known.
        if device==None:
            device=("0x%04x" % deviceid);
        
        return device;
