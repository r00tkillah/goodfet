#!/usr/bin/env python
# GoodFET ARM Client Library
# 
#
# Good luck with alpha / beta code.
# Contributions and bug reports welcome.
#

import sys, binascii, struct
import atlasutils.smartprint as asp
from GoodFET import GoodFET
from intelhex import IntelHex

platforms = {
    "at91sam7": {0:(0x100000, "Flash before remap, SRAM after remap"),
                 0x100000: (0x100000, "Internal Flash"),
                 0x200000: (0x100000, "Internal SRAM"),
                 },
    }
                

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

# ARM7TDMI JTAG commands
GET_DEBUG_CTRL      = 0x80
SET_DEBUG_CTRL      = 0x81
GET_PC              = 0x82
SET_PC              = 0x83
GET_CHIP_ID         = 0x84
GET_DEBUG_STATE     = 0x85
GET_WATCHPOINT      = 0x86
SET_WATCHPOINT      = 0x87
GET_REGISTER        = 0x88
SET_REGISTER        = 0x89
GET_REGISTERS       = 0x8a
SET_REGISTERS       = 0x8b
HALTCPU             = 0x8c
RESUMECPU           = 0x8d
DEBUG_INSTR         = 0x8e      #
STEP_INSTR          = 0x8f      #
STEP_REPLACE        = 0x90      #
PROGRAM_FLASH       = 0x95
LOCKCHIP            = 0x96      # ??
CHIP_ERASE          = 0x97      # can do?
# Really ARM specific stuff
GET_CPSR            = 0x98
SET_CPSR            = 0x99
GET_SPSR            = 0x9a
SET_SPSR            = 0x9b
SET_MODE_THUMB      = 0x9c
SET_MODE_ARM        = 0x9d
SET_IR              = 0x9e
WAIT_DBG            = 0x9f
SHIFT_DR            = 0xa0
SETWATCH0           = 0xa1
SETWATCH1           = 0xa2

PM_usr = 0b10000
PM_fiq = 0b10001
PM_irq = 0b10010
PM_svc = 0b10011
PM_abt = 0b10111
PM_und = 0b11011
PM_sys = 0b11111
proc_modes = {
    PM_usr: ("User Processor Mode", "usr", "Normal program execution mode"),
    PM_fiq: ("FIQ Processor Mode", "fiq", "Supports a high-speed data transfer or channel process"),
    PM_irq: ("IRQ Processor Mode", "irq", "Used for general-purpose interrupt handling"),
    PM_svc: ("Supervisor Processor Mode", "svc", "A protected mode for the operating system"),
    PM_irq: ("Abort Processor Mode", "irq", "Implements virtual memory and/or memory protection"),
    PM_und: ("Undefined Processor Mode", "und", "Supports software emulation of hardware coprocessor"),
    PM_sys: ("System Processor Mode", "sys", "Runs privileged operating system tasks (ARMv4 and above)"),
}

PSR_bits = [ 
    None,
    None,
    None,
    None,
    None,
    "Thumb",
    "nFIQ_int",
    "nIRQ_int",
    "nImprDataAbort_int",
    "BIGendian",
    None,
    None,
    None,
    None,
    None,
    None,
    "GE_0",
    "GE_1",
    "GE_2",
    "GE_3",
    None,
    None,
    None,
    None,
    "Jazelle",
    None,
    None,
    "Q (DSP-overflow)",
    "oVerflow",
    "Carry",
    "Zero",
    "Neg",
    ]



ARM_INSTR_NOP =             0xe1a00000L
ARM_INSTR_BX_R0 =           0xe12fff10L
ARM_INSTR_STR_Rx_r14 =      0xe58f0000L # from atmel docs
ARM_READ_REG =              ARM_INSTR_STR_Rx_r14
ARM_INSTR_LDR_Rx_r14 =      0xe59f0000L # from atmel docs
ARM_WRITE_REG =             ARM_INSTR_LDR_Rx_r14
ARM_INSTR_LDR_R1_r0_4 =     0xe4901004L
ARM_READ_MEM =              ARM_INSTR_LDR_R1_r0_4
ARM_INSTR_STR_R1_r0_4 =     0xe4801004L
ARM_WRITE_MEM =             ARM_INSTR_STR_R1_r0_4
ARM_INSTR_MRS_R0_CPSR =     0xe10f0000L
ARM_INSTR_MSR_cpsr_cxsf_R0 =0xe12ff000L
ARM_INSTR_STMIA_R14_r0_rx = 0xE88E0000L      # add up to 65k to indicate which registers...
ARM_STORE_MULTIPLE =        ARM_INSTR_STMIA_R14_r0_rx
ARM_INSTR_SKANKREGS =       0xE88F7fffL
ARM_INSTR_CLOBBEREGS =      0xE89F7fffL

ARM_INSTR_B_PC =            0xea000000L
ARM_INSTR_BX_PC =           0xe1200010L      # need to set r0 to the desired address
THUMB_INSTR_STR_R0_r0 =     0x60006000L
THUMB_INSTR_MOV_R0_PC =     0x46b846b8L
THUMB_INSTR_BX_PC =         0x47784778L
THUMB_INSTR_NOP =           0x1c001c00L
ARM_REG_PC =                15

ARM7TDMI_IR_EXTEST =            0x0
ARM7TDMI_IR_SCAN_N =            0x2
ARM7TDMI_IR_SAMPLE =            0x3
ARM7TDMI_IR_RESTART =           0x4
ARM7TDMI_IR_CLAMP =             0x5
ARM7TDMI_IR_HIGHZ =             0x7
ARM7TDMI_IR_CLAMPZ =            0x9
ARM7TDMI_IR_INTEST =            0xC
ARM7TDMI_IR_IDCODE =            0xE
ARM7TDMI_IR_BYPASS =            0xF


def PSRdecode(psrval):
    output = [ "(%s mode)"%proc_modes[psrval&0x1f][1] ]
    for x in xrange(5,32):
        if psrval & (1<<x):
            output.append(PSR_bits[x])
    return " ".join(output)
   
fmt = [None, "B", "<H", None, "<L", None, None, None, "<Q"]
def chop(val,byts):
    s = struct.pack(fmt[byts], val)
    return [ord(b) for b in s ]
        
class GoodFETARM(GoodFET):
    """A GoodFET variant for use with ARM7TDMI microprocessor."""
    def ARMhaltcpu(self):
        """Halt the CPU."""
        self.writecmd(0x13,HALTCPU,0,self.data)
        print "CPSR: (%s) %s"%(self.ARMget_regCPSRstr())
    def ARMreleasecpu(self):
        """Resume the CPU."""
        self.writecmd(0x13,RESUMECPU,0,self.data)
    def ARMsetModeArm(self, restart=0):
        self.writecmd(0x13,SET_MODE_ARM,0,[restart])
    def ARMsetModeThumb(self, restart=0):
        self.writecmd(0x13,SET_MODE_THUMB,0,[restart])
    def ARMtest(self):
        #self.ARMreleasecpu()
        #self.ARMhaltcpu()
        print "Status: %s" % self.ARMstatusstr()
        
        #Grab ident three times, should be equal.
        ident1=self.ARMident()
        ident2=self.ARMident()
        ident3=self.ARMident()
        if(ident1!=ident2 or ident2!=ident3):
            print "Error, repeated ident attempts unequal."
            print "%04x, %04x, %04x" % (ident1, ident2, ident3)
        
        #Set and Check Registers
        regs = [1024+x for x in range(0,15)]
        regr = []
        for x in range(len(regs)):
            self.ARMset_register(x, regs[x])

        for x in range(len(regs)):
            regr.append(self.ARMget_register(x))
        
        for x in range(len(regs)):
            if regs[x] != regr[x]:
                print "Error, R%d fail: %x != %x"%(x,regs[x],regr[x])

        return




        #Single step, printing PC.
        print "Tracing execution at startup."
        for i in range(15):
            pc=self.ARMgetPC()
            byte=self.ARMpeekcodebyte(i)
            #print "PC=%04x, %02x" % (pc, byte)
            self.ARMstep_instr()
        
        print "Verifying that debugging a NOP doesn't affect the PC."
        for i in range(1,15):
            pc=self.ARMgetPC()
            self.ARMdebuginstr([NOP])
            if(pc!=self.ARMgetPC()):
                print "ERROR: PC changed during ARMdebuginstr([NOP])!"
        
        print "Checking pokes to XRAM."
        for i in range(0xf000,0xf020):
            self.ARMpokedatabyte(i,0xde)
            if(self.ARMpeekdatabyte(i)!=0xde):
                print "Error in DATA at 0x%04x" % i
        
        #print "Status: %s." % self.ARMstatusstr()
        #Exit debugger
        self.stop()
        print "Done."

    def setup(self):
        """Move the FET into the JTAG ARM application."""
        #print "Initializing ARM."
        self.writecmd(0x13,SETUP,0,self.data)
    def ARMget_dbgstate(self):
        """Read the config register of an ARM."""
        self.writecmd(0x13,GET_DEBUG_STATE,0,self.data)
        retval = struct.unpack("<L", self.data[:4])[0]
        return retval
    def ARMget_dbgctrl(self):
        """Read the config register of an ARM."""
        self.writecmd(0x13,GET_DEBUG_CTRL,0,self.data)
        retval = struct.unpack("B", self.data)[0]
        return retval
    def ARMset_dbgctrl(self,config):
        """Write the config register of an ARM."""
        self.writecmd(0x13,SET_DEBUG_CTRL,1,[config&7])
    #def ARMlockchip(self):
    #    """Set the flash lock bit in info mem."""
    #    self.writecmd(0x13, LOCKCHIP, 0, [])
    

    def ARMidentstr(self):
        ident=self.ARMident()
        ver     = ident >> 28
        partno  = (ident >> 12) & 0x10
        mfgid   = ident & 0xfff
        return "mfg: %x\npartno: %x\nver: %x\n(%x)" % (ver, partno, mfgid, ident); 
    def ARMident(self):
        """Get an ARM's ID."""
        self.writecmd(0x13,GET_CHIP_ID,0,[])
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ARMsetPC(self, val):
        """Set an ARM's PC."""
        self.writecmd(0x13,SET_PC,0,chop(val,4))
    def ARMgetPC(self):
        """Get an ARM's PC."""
        self.writecmd(0x13,GET_PC,0,[])
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ARMget_register(self, reg):
        """Get an ARM's Register"""
        self.writecmd(0x13,GET_REGISTER,1,[reg&0xff])
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ARMset_register(self, reg, val):
        """Get an ARM's Register"""
        self.writecmd(0x13,SET_REGISTER,8,[val&0xff, (val>>8)&0xff, (val>>16)&0xff, val>>24, reg,0,0,0])
        #self.writecmd(0x13,SET_REGISTER,8,[reg,0,0,0, (val>>16)&0xff, val>>24, val&0xff, (val>>8)&0xff])
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ARMget_registers(self):
        """Get ARM Registers"""
        regs = [ self.ARMget_register(x) for x in range(15) ]
        regs.append(self.ARMgetPC())            # make sure we snag the "static" version of PC
        return regs
    def ARMset_registers(self, regs, mask):
        """Set ARM Registers"""
        for x in xrange(15):
          if (1<<x) & mask:
            self.ARMset_register(x,regs.pop())
        if (1<<15) & mask:                      # make sure we set the "static" version of PC or changes will be lost
          self.ARMsetPC(regs.pop())
    def ARMget_regCPSRstr(self):
        psr = self.ARMget_regCPSR()
        return hex(psr), PSRdecode(psr)
    def ARMget_regCPSR(self):
        """Get an ARM's Register"""
        self.writecmd(0x13,GET_CPSR,0,[])
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ARMset_regCPSR(self, val):
        """Get an ARM's Register"""
        self.writecmd(0x13,SET_CPSR,4,[val&0xff, (val>>8)&0xff, (val>>16)&0xff, val>>24])
    def ARMcmd(self,phrase):
        self.writecmd(0x13,READ,len(phrase),phrase)
        val=ord(self.data[0])
        print "Got %02x" % val
        return val
    def ARMdebuginstr(self,instr,bkpt):
        if type (instr) == int or type(instr) == long:
            instr = struct.pack("<L", instr)
        instr = [int("0x%x"%ord(x),16) for x in instr]
        instr.extend([bkpt])
        self.writecmd(0x13,DEBUG_INSTR,len(instr),instr)
        return (self.data)
    def ARM_nop(self, bkpt):
        return self.ARMdebuginstr(ARM_INSTR_NOP, bkpt)
    def ARMset_IR(self, IR):
        self.writecmd(0x13,SET_IR,1, [IR])
        return self.data
    def ARMshiftDR(self, data, bits, LSB, END, RETIDLE):
        self.writecmd(0x13,SHIFT_DR,8,[bits&0xff, LSB&0xff, END&0xff, RETIDLE&0xff, data&0xff,(data>>8)&0xff,(data>>16)&0xff,(data>>24)&0xff])
        return self.data
    def ARMwaitDBG(self, timeout=0xff):
        self.writecmd(0x13,WAIT_DBG,2,[timeout&0xf,timeout>>8])
        return self.data
    def ARMrestart(self):
        self.ARMset_IR(ARM7TDMI_IR_RESTART)
    def ARMset_watchpoint0(self, addr, addrmask, data, datamask, ctrl, ctrlmask):
        self.data = []
        self.data.extend(chop(addr,4))
        self.data.extend(chop(addrmask,4))
        self.data.extend(chop(data,4))
        self.data.extend(chop(datamask,4))
        self.data.extend(chop(ctrl,4))
        self.data.extend(chop(ctrlmask,4))
        self.writecmd(0x13,SETWATCH0,24,self.data)
        return self.data
    def ARMset_watchpoint1(self, addr, addrmask, data, datamask, ctrl, ctrlmask):
        self.data = []
        self.data.extend(chop(addr,4))
        self.data.extend(chop(addrmask,4))
        self.data.extend(chop(data,4))
        self.data.extend(chop(datamask,4))
        self.data.extend(chop(ctrl,4))
        self.data.extend(chop(ctrlmask,4))
        self.writecmd(0x13,SETWATCH1,24,self.data)
        return self.data
    def ARMreadMem(self, adr, wrdcount):
        retval = [] 
        r0 = self.ARMget_register(0);        # store R0 and R1
        r1 = self.ARMget_register(1);
        print >>sys.stderr,("CPSR:\t%x"%self.ARMget_regCPSR())
        for word in range(adr, adr+(wrdcount*4), 4):
            self.ARMset_register(0, word);        # write address into R0
            self.ARM_nop(0)
            self.ARM_nop(1)
            self.ARMdebuginstr(ARM_READ_MEM, 0); # push LDR R1, [R0], #4 into instruction pipeline  (autoincrements for consecutive reads)
            self.ARM_nop(0)
            self.ARMrestart()
            self.ARMwaitDBG()
            print self.ARMget_register(1)


            # FIXME: this may end up changing te current debug-state.  should we compare to current_dbgstate?
            #print repr(self.data[4])
            if (len(self.data)>4 and self.data[4] == '\x00'):
              print >>sys.stderr,("FAILED TO READ MEMORY/RE-ENTER DEBUG MODE")
              raise Exception("FAILED TO READ MEMORY/RE-ENTER DEBUG MODE")
              return (-1);
            else:
              retval.append( self.ARMget_register(1) )  # read memory value from R1 register
              print >>sys.stderr,("CPSR: %x\t\tR0: %x\t\tR1: %x"%(self.ARMget_regCPSR(),self.ARMget_register(0),self.ARMget_register(1)))
        self.ARMset_register(1, r1);       # restore R0 and R1 
        self.ARMset_register(0, r0);
        return retval

    def ARMpeekcodewords(self,adr,words):
        """Read the contents of code memory at an address."""
        self.data=[adr&0xff, (adr>>8)&0xff, (adr>>16)&0xff, (adr>>24)&0xff, words&0xff, (words>>8)&0xff, (words>>16)&0xff, (words>>24)&0xff ]
        self.writecmd(0x13,READ_CODE_MEMORY,8,self.data)
        retval = []
        retval.append(self.serialport.read(words*4))
        #retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return "".join(retval)
    def ARMpeekdatabyte(self,adr):
        """Read the contents of data memory at an address."""
        self.data=[ adr&0xff, (adr>>8)&0xff, (adr>>16)&0xff, (adr>>24)&0xff ]
        self.writecmd(0x13, PEEK, 4, self.data)
        #retval.append(self.serialport.read(words*4))
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ARMpokedatabyte(self,adr,val):
        """Write a byte to data memory."""
        self.data=[adr&0xff, (adr>>8)&0xff, (adr>>16)&0xff, (adr>>24)&0xff, val&0xff, (val>>8)&0xff, (val>>16)&0xff, (val>>24)&0xff ]
        self.writecmd(0x13, POKE, 8, self.data)
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    #def ARMchiperase(self):
    #    """Erase all of the target's memory."""
    #    self.writecmd(0x13,CHIP_ERASE,0,[])
    def ARMstatus(self):
        """Check the status."""
        self.writecmd(0x13,GET_DEBUG_STATE,0,[])
        return ord(self.data[0])
    ARMstatusbits={
                  0x10 : "TBIT",
                  0x08 : "cgenL",
                  0x04 : "Interrupts Enabled (or not?)",
                  0x02 : "DBGRQ",
                  0x01 : "DGBACK"
                  }
    ARMctrlbits={
                  0x04 : "disable interrupts",
                  0x02 : "force dbgrq",
                  0x01 : "force dbgack"
                  }
                  
    def ARMstatusstr(self):
        """Check the status as a string."""
        status=self.ARMstatus()
        str=""
        i=1
        while i<0x100:
            if(status&i):
                str="%s %s" %(self.ARMstatusbits[i],str)
            i*=2
        return str
    def start(self):
        """Start debugging."""
        self.writecmd(0x13,START,0,self.data)
        ident=self.ARMidentstr()
        print "Target identifies as %s." % ident
        print "Debug Status: %s." % self.ARMstatusstr()
        #print "System State: %x." % self.ARMget_regCPSRstr()
        #self.ARMreleasecpu()
        #self.ARMhaltcpu()
        
    def stop(self):
        """Stop debugging."""
        self.writecmd(0x13,STOP,0,self.data)
    #def ARMstep_instr(self):
    #    """Step one instruction."""
    #    self.writecmd(0x13,STEP_INSTR,0,self.data)
    #def ARMflashpage(self,adr):
    #    """Flash 2kB a page of flash from 0xF000 in XDATA"""
    #    data=[adr&0xFF,
    #          (adr>>8)&0xFF,
    #          (adr>>16)&0xFF,
    #          (adr>>24)&0xFF]
    #    print "Flashing buffer to 0x%06x" % adr
    #    self.writecmd(0x13,MASS_FLASH_PAGE,4,data)

    def writecmd(self, app, verb, count=0, data=[]):
        """Write a command and some data to the GoodFET."""
        self.serialport.write(chr(app))
        self.serialport.write(chr(verb))
        count = len(data)
        #if data!=None:
        #    count=len(data); #Initial count ignored.

        #print "TX %02x %02x %04x" % (app,verb,count)

        #little endian 16-bit length
        self.serialport.write(chr(count&0xFF))
        self.serialport.write(chr(count>>8))

        #print "count=%02x, len(data)=%04x" % (count,len(data))

        if count!=0:
            if(isinstance(data,list)):
                for i in range(0,count):
                    #print "Converting %02x at %i" % (data[i],i)
                    data[i]=chr(data[i])
            #print type(data)
            outstr=''.join(data)
            self.serialport.write(outstr)
        if not self.besilent:
            self.readcmd()



