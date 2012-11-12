#!/usr/bin/env python
# GoodFET ARM Client Library
# 
# Contributions and bug reports welcome.
#
# todo:
#  * full cycle debugging.. halt to resume
#  * ensure correct PC handling
#  * flash manipulation (probably need to get the specific chip for this one)
#  * set security (chip-specific)

import sys, binascii, struct, time
from GoodFET import GoodFET
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

# ARM7TDMI JTAG commands
IR_SHIFT =                  0x80
DR_SHIFT =                  0x81
RESETTAP =                  0x82
RESETTARGET =               0x83
DR_SHIFT_MORE =             0x87
GET_REGISTER =              0x8d
SET_REGISTER =              0x8e
DEBUG_INSTR =               0x8f
# Really ARM specific stuff
WAIT_DBG =                  0x91
CHAIN0 =                    0x93
SCANCHAIN1 =                0x94
EICE_READ =                 0x95
EICE_WRITE =                0x96

IR_EXTEST           =  0x0
IR_SCAN_N           =  0x2
IR_SAMPLE           =  0x3
IR_RESTART          =  0x4
IR_CLAMP            =  0x5
IR_HIGHZ            =  0x7
IR_CLAMPZ           =  0x9
IR_INTEST           =  0xC
IR_IDCODE           =  0xE
IR_BYPASS           =  0xF

DBG_DBGACK =    1
DBG_DBGRQ =     2
DBG_IFEN =      4
DBG_cgenL =     8
DBG_TBIT =      16


EICE_DBGCTRL =                     0  # read 3 bit - Debug Control
EICE_DBGCTRL_BITLEN =              3
EICE_DBGSTATUS =                   1  # read 5 bit - Debug Status
EICE_DBGSTATUS_BITLEN =            5
EICE_DBGCCR =                      4  # read 6 bit - Debug Comms Control Register
EICE_DBGCCR_BITLEN =               6
EICE_DBGCDR =                      5  # r/w 32 bit - Debug Comms Data Register
EICE_WP0ADDR =                     8  # r/w 32 bit - Watchpoint 0 Address
EICE_WP0ADDRMASK =                 9  # r/w 32 bit - Watchpoint 0 Addres Mask
EICE_WP0DATA =                     10 # r/w 32 bit - Watchpoint 0 Data
EICE_WP0DATAMASK =                 11 # r/w 32 bit - Watchpoint 0 Data Masl
EICE_WP0CTRL =                     12 # r/w 9 bit - Watchpoint 0 Control Value
EICE_WP0CTRLMASK =                 13 # r/w 8 bit - Watchpoint 0 Control Mask
EICE_WP1ADDR =                     16 # r/w 32 bit - Watchpoint 0 Address
EICE_WP1ADDRMASK =                 17 # r/w 32 bit - Watchpoint 0 Addres Mask
EICE_WP1DATA =                     18 # r/w 32 bit - Watchpoint 0 Data
EICE_WP1DATAMASK =                 19 # r/w 32 bit - Watchpoint 0 Data Masl
EICE_WP1CTRL =                     20 # r/w 9 bit - Watchpoint 0 Control Value
EICE_WP1CTRLMASK =                 21 # r/w 8 bit - Watchpoint 0 Control Mask

MSB         = 0
LSB         = 1
NOEND       = 2
NORETIDLE   = 4

F_TBIT      = 1<<40

PM_usr = 0b10000
PM_fiq = 0b10001
PM_irq = 0b10010
PM_svc = 0b10011
PM_abt = 0b10111
PM_und = 0b11011
PM_sys = 0b11111
proc_modes = {
    0:      ("UNKNOWN, MESSED UP PROCESSOR MODE","fsck", "This should Never happen.  MCU is in funky state!"),
    PM_usr: ("User Processor Mode", "usr", "Normal program execution mode"),
    PM_fiq: ("FIQ Processor Mode", "fiq", "Supports a high-speed data transfer or channel process"),
    PM_irq: ("IRQ Processor Mode", "irq", "Used for general-purpose interrupt handling"),
    PM_svc: ("Supervisor Processor Mode", "svc", "A protected mode for the operating system"),
    PM_abt: ("Abort Processor Mode", "abt", "Implements virtual memory and/or memory protection"),
    PM_und: ("Undefined Processor Mode", "und", "Supports software emulation of hardware coprocessor"),
    PM_sys: ("System Processor Mode", "sys", "Runs privileged operating system tasks (ARMv4 and above)"),
}

PSR_bits = [ 
    None, None, None, None, None, "Thumb", "nFIQ_int", "nIRQ_int", 
    "nImprDataAbort_int", "BIGendian", None, None, None, None, None, None, 
    "GE_0", "GE_1", "GE_2", "GE_3", None, None, None, None, 
    "Jazelle", None, None, "Q (DSP-overflow)", "oVerflow", "Carry", "Zero", "Neg",
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
ARM_INSTR_STRB_R1_r0_1 =    0xe4c01001L
ARM_WRITE_MEM_BYTE =        ARM_INSTR_STRB_R1_r0_1
ARM_INSTR_MRS_R0_CPSR =     0xe10f0000L
ARM_INSTR_MSR_cpsr_cxsf_R0 =0xe12ff000L
ARM_INSTR_STMIA_R14_r0_rx = 0xE88e0000L      # add up to 65k to indicate which registers...
ARM_INSTR_LDMIA_R14_r0_rx = 0xE89e0000L      # add up to 65k to indicate which registers...
ARM_STORE_MULTIPLE =        ARM_INSTR_STMIA_R14_r0_rx
ARM_INSTR_SKANKREGS =       0xE88F7fffL
ARM_INSTR_CLOBBEREGS =      0xE89F7fffL

ARM_INSTR_B_IMM =           0xea000000L
ARM_INSTR_B_PC =            0xea000000L
ARM_INSTR_BX_PC =           0xe1200010L      # need to set r0 to the desired address
THUMB_INSTR_LDR_R0_r0 =     0x68006800L
THUMB_WRITE_REG =           THUMB_INSTR_LDR_R0_r0
THUMB_INSTR_STR_R0_r0 =     0x60006000L
THUMB_READ_REG =            THUMB_INSTR_STR_R0_r0
THUMB_INSTR_MOV_R0_PC =     0x46b846b8L
THUMB_INSTR_MOV_PC_R0 =     0x46474647L
THUMB_INSTR_BX_PC =         0x47784778L
THUMB_INSTR_NOP =           0x1c001c00L
THUMB_INSTR_B_IMM =         0xe000e000L
ARM_REG_PC =                15

nRW         = 0
MAS0        = 1
MAS1        = 2
nOPC        = 3
nTRANS      = 4
EXTERN      = 5
CHAIN       = 6
RANGE       = 7
ENABLE      = 8

DBGCTRLBITS = {
        'nRW':nRW,
        'MAS0':MAS0,
        'MAS1':MAS1,
        'nOPC':nOPC,
        'nTRANS':nTRANS,
        'EXTERN':EXTERN,
        'CHAIN':CHAIN,
        'RANGE':RANGE,
        'ENABLE':ENABLE,
        1<<nRW:'nRW',
        1<<MAS0:'MAS0',
        1<<MAS1:'MAS1',
        1<<nOPC:'nOPC',
        1<<nTRANS:'nTRANS',
        1<<EXTERN:'EXTERN',
        1<<CHAIN:'CHAIN',
        1<<RANGE:'RANGE',
        1<<ENABLE:'ENABLE',
        }

LDM_BITMASKS = [(1<<x)-1 for x in xrange(16)]
#### TOTALLY BROKEN, NEED VALIDATION AND TESTING
PCOFF_DBGRQ = 4 * 4
PCOFF_WATCH = 4 * 4
PCOFF_BREAK = 4 * 4


def debugstr(strng):
    print >>sys.stderr,(strng)
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
    def __init__(self):
        GoodFET.__init__(self)
        self.storedPC =         0xffffffff
        self.current_dbgstate = 0xffffffff
        self.flags =            0xffffffff
        self.nothing =          0xffffffff
    def __del__(self):
        try:
            if (self.ARMget_dbgstate()&9) == 9:
                self.resume()
        except:
            sys.excepthook(*sys.exc_info())
    def setup(self):
        """Move the FET into the JTAG ARM application."""
        #print "Initializing ARM."
        self.writecmd(0x13,SETUP,0,self.data)
    def flash(self,file):
        """Flash an intel hex file to code memory."""
        print "Flash not implemented.";
    def dump(self,fn,start=0,stop=0xffffffff):
        """Dump an intel hex file from code memory."""
        
        print "Dumping from %04x to %04x as %s." % (start,stop,f);
        # FIXME: get mcu state and return it to that state
        self.halt()

        h = IntelHex(None);
        i=start;
        while i<=stop:
            data=self.ARMreadChunk(i, 48, verbose=0);
            print "Dumped %06x."%i;
            for dword in data:
                if i<=stop and dword != 0xdeadbeef:
                    h.puts( i, struct.pack("<I", dword) )
                i+=4;
        # FIXME: get mcu state and return it to that state
        self.resume()
        h.write_hex_file(fn);

        print "Dump not implemented.";
    def ARMshift_IR(self, IR, noretidle=0):
        self.writecmd(0x13,IR_SHIFT,2, [IR, LSB|noretidle])
        return self.data
    def ARMshift_DR(self, data, bits, flags):
        self.writecmd(0x13,DR_SHIFT,14,[bits&0xff, flags&0xff, 0, 0, data&0xff,(data>>8)&0xff,(data>>16)&0xff,(data>>24)&0xff, (data>>32)&0xff,(data>>40)&0xff,(data>>48)&0xff,(data>>56)&0xff,(data>>64)&0xff,(data>>72)&0xff])
        return self.data
    def ARMshift_DR_more(self, data, bits, flags):
        self.writecmd(0x13,DR_SHIFT_MORE,14,[bits&0xff, flags&0xff, 0, 0, data&0xff,(data>>8)&0xff,(data>>16)&0xff,(data>>24)&0xff, (data>>32)&0xff,(data>>40)&0xff,(data>>48)&0xff,(data>>56)&0xff,(data>>64)&0xff,(data>>72)&0xff])
        return self.data
    def ARMwaitDBG(self, timeout=0xff):
        self.current_dbgstate = self.ARMget_dbgstate()
        while ( not ((self.current_dbgstate & 9L) == 9)):
            timeout -=1
            self.current_dbgstate = self.ARMget_dbgstate()
        return timeout
    def ARMident(self):
        """Get an ARM's ID."""
        self.ARMshift_IR(IR_IDCODE,0)
        self.ARMshift_DR(0,32,LSB)
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ARMidentstr(self):
        ident=self.ARMident()
        ver     = (ident >> 28)
        partno  = (ident >> 12) & 0xffff
        mfgid   = (ident >> 1)  & 0x7ff
        return "Chip IDCODE: 0x%x\n\tver: %x\n\tpartno: %x\n\tmfgid: %x\n" % (ident, ver, partno, mfgid); 
    def ARMeice_write(self, reg, val):
        data = chop(val,4)
        data.extend([reg])
        retval = self.writecmd(0x13, EICE_WRITE, 5, data)
        return retval
    def ARMeice_read(self, reg):
        self.writecmd(0x13, EICE_READ, 1, [reg])
        retval, = struct.unpack("<L",self.data)
        return retval
    def ARMget_dbgstate(self):
        """Read the config register of an ARM."""
        self.ARMeice_read(EICE_DBGSTATUS)
        self.current_dbgstate = struct.unpack("<L", self.data[:4])[0]
        return self.current_dbgstate
    status = ARMget_dbgstate
    def statusstr(self):
        """Check the status as a string."""
        status=self.status()
        str=""
        i=1
        while i<0x20:
            if(status&i):
                str="%s %s" %(self.ARMstatusbits[i],str)
            i*=2
        return str
    def ARMget_dbgctrl(self):
        """Read the config register of an ARM."""
        self.ARMeice_read(EICE_DBGCTRL)
        retval = struct.unpack("<L", self.data[:4])[0]
        return retval
    def ARMset_dbgctrl(self,config):
        """Write the config register of an ARM."""
        self.ARMeice_write(EICE_DBGCTRL, config&7)
    def ARMgetPC(self):
        """Get an ARM's PC. Note: real PC gets all wonky in debug mode, this is the "saved" PC"""
        return self.storedPC
    getpc = ARMgetPC
    def ARMsetPC(self, val):
        """Set an ARM's PC.  Note: real PC gets all wonky in debug mode, this changes the "saved" PC which is used when exiting debug mode"""
        self.storedPC = val
    def ARMget_register(self, reg):
        """Get an ARM's Register"""
        self.writecmd(0x13,GET_REGISTER,1,[reg&0xf])
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ARMset_register(self, reg, val):
        """Get an ARM's Register"""
        self.writecmd(0x13,SET_REGISTER,8,[val&0xff, (val>>8)&0xff, (val>>16)&0xff, val>>24, reg,0,0,0])
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
            self.ARMset_register(x,regs.pop(0))
        if (1<<15) & mask:                      # make sure we set the "static" version of PC or changes will be lost
          self.ARMsetPC(regs.pop(0))
    def ARMdebuginstr(self,instr,bkpt):
        if type (instr) == int or type(instr) == long:
            instr = struct.pack("<L", instr)
        instr = [int("0x%x"%ord(x),16) for x in instr]
        instr.extend([bkpt])
        self.writecmd(0x13,DEBUG_INSTR,len(instr),instr)
        return (self.data)
    def ARM_nop(self, bkpt=0):
        if self.status() & DBG_TBIT:
            return self.ARMdebuginstr(THUMB_INSTR_NOP, bkpt)
        return self.ARMdebuginstr(ARM_INSTR_NOP, bkpt)
    def ARMrestart(self):
        self.ARMshift_IR(IR_RESTART)
    def ARMset_watchpoint0(self, addr, addrmask, data, datamask, ctrl, ctrlmask):
        self.ARMeice_write(EICE_WP0ADDR, addr);           # write 0 in watchpoint 0 address
        self.ARMeice_write(EICE_WP0ADDRMASK, addrmask);   # write 0xffffffff in watchpoint 0 address mask
        self.ARMeice_write(EICE_WP0DATA, data);           # write 0 in watchpoint 0 data
        self.ARMeice_write(EICE_WP0DATAMASK, datamask);   # write 0xffffffff in watchpoint 0 data mask
        self.ARMeice_write(EICE_WP0CTRL, ctrl);           # write 0x00000100 in watchpoint 0 control value register (enables watchpoint)
        self.ARMeice_write(EICE_WP0CTRLMASK, ctrlmask);   # write 0xfffffff7 in watchpoint 0 control mask - only detect the fetch instruction
        return self.data
    def ARMset_watchpoint1(self, addr, addrmask, data, datamask, ctrl, ctrlmask):
        self.ARMeice_write(EICE_WP1ADDR, addr);           # write 0 in watchpoint 1 address
        self.ARMeice_write(EICE_WP1ADDRMASK, addrmask);   # write 0xffffffff in watchpoint 1 address mask
        self.ARMeice_write(EICE_WP1DATA, data);           # write 0 in watchpoint 1 data
        self.ARMeice_write(EICE_WP1DATAMASK, datamask);   # write 0xffffffff in watchpoint 1 data mask
        self.ARMeice_write(EICE_WP1CTRL, ctrl);           # write 0x00000100 in watchpoint 1 control value register (enables watchpoint)
        self.ARMeice_write(EICE_WP1CTRLMASK, ctrlmask);   # write 0xfffffff7 in watchpoint 1 control mask - only detect the fetch instruction
        return self.data
    def THUMBgetPC(self):
        THUMB_INSTR_STR_R0_r0 =     0x60006000L
        THUMB_INSTR_MOV_R0_PC =     0x46b846b8L
        THUMB_INSTR_BX_PC =         0x47784778L
        THUMB_INSTR_NOP =           0x1c001c00L

        r0 = self.ARMget_register(0)
        self.ARMdebuginstr(THUMB_INSTR_MOV_R0_PC, 0)
        retval = self.ARMget_register(0)
        self.ARMset_register(0,r0)
        return retval
    def ARMcapture_system_state(self, pcoffset):
        if self.ARMget_dbgstate() & DBG_TBIT:
            pcoffset += 8
        else:
            pcoffset += 4
        self.storedPC = self.ARMget_register(15) + pcoffset
        self.last_dbg_state = self.ARMget_dbgstate()
    def ARMhaltcpu(self):
        """Halt the CPU."""
        if not(self.ARMget_dbgstate()&1):
            self.ARMset_dbgctrl(2)
            if (self.ARMwaitDBG() == 0):
                raise Exception("Timeout waiting to enter DEBUG mode on HALT")
            self.ARMset_dbgctrl(0)
            self.ARMcapture_system_state(PCOFF_DBGRQ)
            if self.last_dbg_state&0x10:
                self.storedPC = self.THUMBgetPC()
            else:
                self.storedPC = self.ARMget_register(15)
        self.storedPC, self.flags, self.nothing = self.ARMchain0(0)
        if self.ARMget_dbgstate() & DBG_TBIT:
            self.ARMsetModeARM()
            if self.storedPC ^ 4:
                self.ARMset_register(15,self.storedPC&0xfffffffc)
        print "CPSR: (%s) %s"%(self.ARMget_regCPSRstr())
    halt = ARMhaltcpu

    def ARMreleasecpu(self):
        """Resume the CPU."""
        # restore registers FIXME: DO THIS
        if self.ARMget_dbgstate()&1 == 0:
            return
        currentPC, self.currentflags, nothing = self.ARMchain0(self.storedPC,self.flags)
        if not(self.flags & F_TBIT):                                    # need to be in arm mode
            if self.currentflags & F_TBIT:                              # currently in thumb mode
                self.ARMsetModeARM()
            # branch to the right address
            self.ARMset_register(15, self.storedPC)
            #print hex(self.storedPC)
            #print hex(self.ARMget_register(15))
            #print hex(self.ARMchain0(self.storedPC,self.flags)[0])
            self.ARMchain0(self.storedPC,self.flags)
            self.ARM_nop(0)
            self.ARM_nop(1)
            self.ARMdebuginstr(ARM_INSTR_B_IMM | 0xfffff0,0)
            self.ARM_nop(0)
            self.ARMrestart()

        elif self.flags & F_TBIT:                                       # need to be in thumb mode
            if not (self.currentflags & F_TBIT):                        # currently in arm mode
                self.ARMsetModeThumb()
            r0=self.ARMget_register(0)
            self.ARMset_register(0, self.storedPC)
            self.ARMdebuginstr(THUMB_INSTR_MOV_PC_R0,0)
            self.ARM_nop(0)
            self.ARM_nop(1)
            #print hex(self.storedPC)
            #print hex(self.ARMget_register(15))
            print hex(self.ARMchain0(self.storedPC,self.flags)[0])
            self.ARMdebuginstr(THUMB_INSTR_B_IMM | (0x7fc07fc),0)
            self.ARM_nop(0)
            self.ARMrestart()

    resume = ARMreleasecpu
    
    def resettap(self):
        self.writecmd(0x13, RESETTAP, 0,[])
    def ARMsetModeARM(self):
        r0 = None
        if ((self.current_dbgstate & DBG_TBIT)):
            debugstr("=== Switching to ARM mode ===")
            self.ARM_nop(0)
            self.ARMdebuginstr(THUMB_INSTR_BX_PC,0)
            self.ARM_nop(0)
            self.ARM_nop(0)
        self.resettap()
        self.current_dbgstate = self.ARMget_dbgstate();
        return self.current_dbgstate
    def ARMsetModeThumb(self):                               # needs serious work and truing
        self.resettap()
        debugstr("=== Switching to THUMB mode ===")
        if ( not (self.current_dbgstate & DBG_TBIT)):
            self.storedPC |= 1
            r0 = self.ARMget_register(0)
            self.ARMset_register(0, self.storedPC)
            self.ARM_nop(0)
            self.ARMdebuginstr(ARM_INSTR_BX_R0,0)
            self.ARM_nop(0)
            self.ARM_nop(0)
            self.resettap()
            self.ARMset_register(0,r0)
        self.current_dbgstate = self.ARMget_dbgstate();
        return self.current_dbgstate
    def ARMget_regCPSRstr(self):
        psr = self.ARMget_regCPSR()
        return hex(psr), PSRdecode(psr)
    def ARMget_regCPSR(self):
        """Get an ARM's Register"""
        r0 = self.ARMget_register(0)
        self.ARM_nop( 0) # push nop into pipeline - clean out the pipeline...
        self.ARMdebuginstr(ARM_INSTR_MRS_R0_CPSR, 0) # push MRS_R0, CPSR into pipeline - fetch
        self.ARM_nop( 0) # push nop into pipeline - decoded
        self.ARM_nop( 0) # push nop into pipeline - execute
        retval = self.ARMget_register(0)
        self.ARMset_register(0, r0)
        return retval
    def ARMset_regCPSR(self, val):
        """Get an ARM's Register"""
        r0 = self.ARMget_register(0)
        self.ARMset_register(0, val)
        self.ARM_nop( 0)        # push nop into pipeline - clean out the pipeline...
        self.ARMdebuginstr(ARM_INSTR_MSR_cpsr_cxsf_R0, 0) # push MSR cpsr_cxsf, R0 into pipeline - fetch
        self.ARM_nop( 0)        # push nop into pipeline - decoded
        self.ARM_nop( 0)        # push nop into pipeline - execute
        self.ARMset_register(0, r0)
        return(val)
    def ARMreadMem(self, adr, wrdcount=1):
        retval = [] 
        r0 = self.ARMget_register(0);        # store R0 and R1
        r1 = self.ARMget_register(1);
        #print >>sys.stderr,("CPSR:\t%x"%self.ARMget_regCPSR())
        self.ARMset_register(0, adr);        # write address into R0
        self.ARMset_register(1, 0xdeadbeef)
        for word in range(adr, adr+(wrdcount*4), 4):
            #sys.stdin.readline()
            self.ARM_nop(0)
            self.ARM_nop(1)
            self.ARMdebuginstr(ARM_READ_MEM, 0); # push LDR R1, [R0], #4 into instruction pipeline  (autoincrements for consecutive reads)
            self.ARM_nop(0)
            self.ARMrestart()
            self.ARMwaitDBG()
            #print hex(self.ARMget_register(1))

            # FIXME: this may end up changing te current debug-state.  should we compare to current_dbgstate?
            #print repr(self.data[4])
            if (len(self.data)>4 and self.data[4] == '\x00'):
              print >>sys.stderr,("FAILED TO READ MEMORY/RE-ENTER DEBUG MODE")
              raise Exception("FAILED TO READ MEMORY/RE-ENTER DEBUG MODE")
              return (-1);
            else:
              retval.append( self.ARMget_register(1) )  # read memory value from R1 register
              #print >>sys.stderr,("CPSR: %x\t\tR0: %x\t\tR1: %x"%(self.ARMget_regCPSR(),self.ARMget_register(0),self.ARMget_register(1)))
        self.ARMset_register(1, r1);       # restore R0 and R1 
        self.ARMset_register(0, r0);
        return retval
    def ARMreadChunk(self, adr, wordcount, verbose=1):         
        """ Only works in ARM mode currently
        WARNING: Addresses must be word-aligned!
        """
        regs = self.ARMget_registers()
        self.ARMset_registers([0xdeadbeef for x in xrange(14)], 0xe)
        output = []
        count = wordcount
        while (wordcount > 0):
            if (verbose and wordcount%64 == 0):  sys.stderr.write(".")
            count = (wordcount, 0xe)[wordcount>0xd]
            bitmask = LDM_BITMASKS[count]
            self.ARMset_register(14,adr)
            self.ARM_nop(1)
            self.ARMdebuginstr(ARM_INSTR_LDMIA_R14_r0_rx | bitmask ,0)
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
    def ARMreadStream(self, adr, bytecount):
        data = [struct.unpack("<L", x) for x in self.ARMreadChunk(adr, (bytecount-1/4)+1)]
        return "".join(data)[:bytecount]
        
    def ARMwriteChunk(self, adr, wordarray):         
        """ Only works in ARM mode currently
        WARNING: Addresses must be word-aligned!
        """
        regs = self.ARMget_registers()
        wordcount = len(wordarray)
        while (wordcount > 0):
            if (wordcount%64 == 0):  sys.stderr.write(".")
            count = (wordcount, 0xe)[wordcount>0xd]
            bitmask = LDM_BITMASKS[count]
            self.ARMset_register(14,adr)
            #print len(wordarray),bin(bitmask)
            self.ARMset_registers(wordarray[:count],bitmask)
            self.ARM_nop(1)
            self.ARMdebuginstr(ARM_INSTR_STMIA_R14_r0_rx | bitmask ,0)
            #FIXME: do we need the extra nop here?
            self.ARMrestart()
            self.ARMwaitDBG()
            wordarray = wordarray[count:]
            wordcount -= count
            adr += count*4
            #print hex(adr)
        # FIXME: handle the rest of the wordcount here.
    def ARMwriteMem(self, adr, wordarray, instr=ARM_WRITE_MEM):
        r0 = self.ARMget_register(0);        # store R0 and R1
        r1 = self.ARMget_register(1);
        #print >>sys.stderr,("CPSR:\t%x"%self.ARMget_regCPSR())
        for widx in xrange(len(wordarray)):
            address = adr + (widx*4)
            word = wordarray[widx]
            self.ARMset_register(0, address);        # write address into R0
            self.ARMset_register(1, word);        # write address into R0
            self.ARM_nop(0)
            self.ARM_nop(1)
            self.ARMdebuginstr(instr, 0); # push STR R1, [R0], #4 into instruction pipeline  (autoincrements for consecutive writes)
            self.ARM_nop(0)
            self.ARMrestart()
            self.ARMwaitDBG()
            #print >>sys.stderr,hex(self.ARMget_register(1))
        self.ARMset_register(1, r1);       # restore R0 and R1 
        self.ARMset_register(0, r0);
    def writeMemByte(self, adr, byte):
        self.ARMwriteMem(adr, byte, ARM_WRITE_MEM_BYTE)


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
    def ARMresettarget(self, delay=1000):
        return self.writecmd(0x13,RESETTARGET,2, [ delay&0xff, (delay>>8)&0xff ] )

    def ARMchain0(self, address, bits=0x819684c054, data=0):
        bulk = chop(address,4)
        bulk.extend(chop(bits,8))
        bulk.extend(chop(data,4))
        #print >>sys.stderr,(repr(bulk))
        self.writecmd(0x13,CHAIN0,16,bulk)
        d1,b1,a1 = struct.unpack("<LQL",self.data)
        return (a1,b1,d1)

    def start(self):
        """Start debugging."""
        self.writecmd(0x13,START,0,self.data)
        print >>sys.stderr,"Identifying Target:"
        ident=self.ARMidentstr()
        print >>sys.stderr,ident
        print >>sys.stderr,"Debug Status:\t%s\n" % self.statusstr()

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


