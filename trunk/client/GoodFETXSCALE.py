#!/usr/bin/env python
# GoodFET Client Library
# 
#
# Good luck with alpha / beta code.
# Contributions and bug reports welcome.
#
# NOTE: this is just a hacked up copy of the GoodFETARM.py file

import sys, binascii, struct

# Standard verbs
READ  = 0x00
WRITE = 0x01
PEEK  = 0x02
POKE  = 0x03
SETUP = 0x10
START = 0x20
STOP  = 0x21
CALL  = 0x30
EXEC  = 0x31
NOK   = 0x7E
OK    = 0x7F

# XSCALE JTAG verbs
GET_CHIP_ID         = 0xF1

from GoodFET import GoodFET
from intelhex import IntelHex

class GoodFETXSCALE(GoodFET):

    """A GoodFET variant for use with XScale processors."""

    XSCALEAPP=0x13;
    APP=XSCALEAPP;
 
    def setup(self):
        """Move the FET into the JTAG ARM application."""
        print "Initializing XScale..."
        self.writecmd(self.APP, SETUP, 0, self.data)

    def start(self):
        """Start debugging."""
        print "Staring debug..."
        self.writecmd(self.APP, START, 0, self.data)

    def stop(self):
        """Stop debugging."""
        print "Stopping debug..."
        self.writecmd(self.APP, STOP, 0, self.data)

    def get_id(self):
        """Get the Chip ID."""
        
        # send the get chip ID command
        self.writecmd(self.APP, GET_CHIP_ID, 0, [])

        # get the response
        ident = struct.unpack("<L", "".join(self.data[0:4]))[0]

        version = ident >> 28
        part_number = (ident >> 12) & 0x10
        manufacturer = ident & 0xFFF

        print "XScale ID --\n\tmfg: %x\n\tpart: %x\n\tver: %x\n\t(%x)" % (version, part_number, manufacturer, ident)

        return ident
    

