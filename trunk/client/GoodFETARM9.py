#!/usr/bin/env python
# GoodFET ARM9 Client Library
# 
# Contributions and bug reports welcome.
#
# todo:
#  * full cycle debugging.. halt to resume
#  * ensure correct PC handling
#  * flash manipulation (probably need to get the specific chip for this one)
#  * set security (chip-specific)

import sys, binascii, struct, time
import atlasutils.smartprint as asp
from GoodFET import GoodFET
import GoodFETARM7
from intelhex import IntelHex


#Global Commands
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

# ARM JTAG commands
IR_SHIFT =                  0x80
DR_SHIFT =                  0x81
RESETTAP =                  0x82
RESETTARGET =               0x83
GET_REGISTER =              0x87
SET_REGISTER =              0x88
DEBUG_INSTR =               0x89
# Really ARM specific stuff
WAIT_DBG =                  0x91
CHAIN0 =                    0x93
SCANCHAIN1 =                0x94
EICE_READ =                 0x95
EICE_WRITE =                0x96


class GoodFETARM9(GoodFETARM7.GoodFETARM7):
    def ARM9readMem(self, adr, wordcount):
        """ Only works in ARM mode currently
        WARNING: Addresses must be word-aligned!
        """
        regs = self.ARMget_registers()
        self.ARMset_registers([0xdeadbeef for x in xrange(14)], 0xe)
        output = []
        count = wordcount
        while (wordcount > 0):
            count = (wordcount, 0xe)[wordcount>0xd]
            bitmask = LDM_BITMASKS[count]
            self.ARMset_register(14,adr)
            self.ARMdebuginstr(ARM_INSTR_LDMIA_R14_r0_rx | bitmask ,0)
            self.ARM_nop(1)
            #FIXME: do we need the extra nop here?
            self.ARMrestart()
            self.ARMwaitDBG()
            output.extend([self.ARMget_register(x) for x in xrange(count)])
            wordcount -= count
            adr += count*4
            #print hex(adr)
        # FIXME: handle the rest of the wordcount here.
        self.ARMset_registers(regs,0xe)
        return output
