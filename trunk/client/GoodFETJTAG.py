#!/usr/bin/env python
# GoodFET Basic JTAG Client

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

from GoodFET import GoodFET
from intelhex import IntelHex

class GoodFETJTAG(GoodFET):

    """A GoodFET variant for basic JTAG'ing."""

    JTAGAPP=0x10;
    APP=JTAGAPP;
 
    def setup(self):
        """Move the FET into the JTAG configuration."""
        print "Initializing JTAG..."
        #self.writecmd(self.APP, SETUP, 0, self.data)

    def detect(self):
        """Detect the JTAG IR width."""
        pass


