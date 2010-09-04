from GoodFETARM7 import *
"""
This is the ARM7 series of microcontrollers from Atmel, including:
* AT91M40800
* AT91R40807
* AT91M40807
* AT91R40008

"""
##### FLASH UPLOADER CODE
EBI_BASE =       0xFFE00000
EBI_OFF_CSR0 =   0x0
EBI_OFF_CSR1 =   0x4
EBI_OFF_CSR2 =   0x8
EBI_OFF_CSR3 =   0xc
EBI_OFF_CSR4 =   0x10
EBI_OFF_CSR5 =   0x14
EBI_OFF_CSR6 =   0x18
EBI_OFF_CSR7 =   0x1c
EBI_CSR0_MASK =  0xFFFF0000
EBI_OFF_RCR =    0x20
EBI_OFF_MCR =    0x24

EBI_CSR0 =      EBI_BASE + EBI_OFF_CSR0
EBI_CSR1 =      EBI_BASE + EBI_OFF_CSR1
EBI_CSR2 =      EBI_BASE + EBI_OFF_CSR2
EBI_CSR3 =      EBI_BASE + EBI_OFF_CSR3
EBI_CSR4 =      EBI_BASE + EBI_OFF_CSR4
EBI_CSR5 =      EBI_BASE + EBI_OFF_CSR5
EBI_CSR6 =      EBI_BASE + EBI_OFF_CSR6
EBI_CSR7 =      EBI_BASE + EBI_OFF_CSR7
EBI_MCR =       EBI_BASE + EBI_OFF_MCR

REMAP_CMD =      0x00000001
MEM_CTRL_VAL =   0x00000006


SF_CHIP_ID =     0xFFF00000         # AT91R40 series, not sure on others
SF_CIDR_MASK =   0x0FFFFF00

PS_BASE =        0xFFFF4000
PS_CR =          PS_BASE
PS_PCER =        PS_BASE + 0x4
PS_PCDR =        PS_BASE + 0x8
PS_PCSR =        PS_BASE + 0xC
PS_US0 =         1<<2
PS_US1 =         1<<3
PS_TC0 =         1<<4
PS_TC1 =         1<<5
PS_TC2 =         1<<6
PS_PIO =         1<<8

AIC_INT_SOURCES = (
        ("FIQ","Fast Interrupt"),
        ("SWIRQ","Software Interrupt"),
        ("US0IRQ","USART Channel 0 Interrupt"),
        ("US1IRQ","USART Channel 1 Interrupt"),
        ("TC0IRQ","Timer Channel 0 Interrupt"),
        ("TC1IRQ","Timer Channel 1 Interrupt"),
        ("TC2IRQ","Timer Channel 2 Interrupt"),
        ("WDIRQ", "Watchdog Interrupt"),
        ("PIOIRQ","Parallel I/O Controller Interrupt"),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        ("IRQ0","External Interrupt 0"),
        ("IRQ1","External Interrupt 0"),
        ("IRQ0","External Interrupt 0"),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        )

def aic_smr_decode(smr):
    output = ["Interrupt Priority: %s"%(smr&7),
            "Interrupt Source Type: %s"%("Low Level Sensitive","Negative Edge Triggered","High Level Sensitive","Positive Edge Triggered")[(smr>>5)],
            ]
    return "\n".join(output)

AIC_BASE = 0xFFFFF000
AIC_SMR = [(AIC_BASE+(x*4), "Source Mode Register %d"%x)  for x in xrange(32)]
AIC_SVR = [(AIC_BASE+0x80+(x*4), "Source Vector Register %d"%x)  for x in xrange(32)]
AIC_IVR = AIC_BASE + 0x100
AIC_FVR = AIC_BASE + 0x104
AIC_ISR = AIC_BASE + 0x108
AIC_IPR = AIC_BASE + 0x10c
AIC_IMR = AIC_BASE + 0x110
AIC_CISR = AIC_BASE + 0x114
AIC_IECR = AIC_BASE + 0x120
AIC_IDCR = AIC_BASE + 0x124
AIC_ICCR = AIC_BASE + 0x128
AIC_ISCR = AIC_BASE + 0x12c
AIC_EOICR = AIC_BASE + 0x130
AIC_SPU = AIC_BASE + 0x134


PIO_BASE = 0xFFFF0000
PIO_PER =   PIO_BASE + 0x0
PIO_PDR =   PIO_BASE + 0x4
PIO_PSR =   PIO_BASE + 0x8
PIO_OER =   PIO_BASE + 0x10
PIO_ODR =   PIO_BASE + 0x14
PIO_OSR =   PIO_BASE + 0x18
PIO_SODR =  PIO_BASE + 0x30
PIO_CODR =  PIO_BASE + 0x34
PIO_ODSR =  PIO_BASE + 0x38
PIO_CDSR =  PIO_BASE + 0x3c
PIO_IER =   PIO_BASE + 0x40
PIO_IDR =   PIO_BASE + 0x44
PIO_IMR =   PIO_BASE + 0x48
PIO_ISR =   PIO_BASE + 0x4c

WD_BASE = 0xFFFF8000
WD_OMR  =   WD_BASE + 0x0
WD_CMR  =   WD_BASE + 0x4
WD_CR   =   WD_BASE + 0x8
WD_SR   =   WD_BASE + 0xc

SF_BASE = 0xFFF00000
SF_CIDR =   SF_BASE + 0x0
SF_EXID =   SF_BASE + 0x4
SF_RSR =    SF_BASE + 0x8
SF_MMR =    SF_BASE + 0xC
SF_PMR =    SF_BASE + 0x18

#* Flash
FLASH_BASE_ADDR =    0x1000000
WAIT =               300000
FLASH_CODE_MASK =    0x000000FF

#*Flash AT49 codes
ATMEL_MANUFACTURED =         0x001F
FLASH_AT49BV_UNKNOW =        0xFFFF
FLASH_AT49BV8011 =           0x00CB
FLASH_AT49BV8011T =          0x004A
FLASH_AT49BV16x4 =           0x00C0
FLASH_AT49BV16x4T =          0x00C2

#*Flash AT29 codes
FLASH_AT29LV1024 =               0X26
FLASH_AT29C020 =                 0XDA

#* Flash Program information
FLASH_PRG_SIZE =     0x800   #* 2Kbytes
FLASH_PRG_DEST =     0x20    #* Address on the target
START_PRG =          0x20

#* Parameter for Flash_XV_Send_Data functions
ERASE =  1
PROGRAM =0

MIRROR =     1
NO_MIRROR =  0

ERASE_DATA = 0

#* Load program parameters
NB_REG =     13
SIZE_DATA =  4

#* Flash LV Send Data parameters
SIZE_256_BYTES = 0x100
PACKET_SIZE =64

NB_PRG =     3

#* Periph
EBI =    0
PLL =    1

#* Targets
EB40 =   0x04080700
EB40A =  0x04000800
EB42 =   0x04280000
EB55 =   0x05580000
EB63 =   0x06320000
EBMASK = 0x0fffff00

NB_TARGET_SUPPORTED =    6

#* Flash type
FLASH_LV =   0
FLASH_BV =   1

#* Flash Program Address 
FLASH_LV_PRG =   0x01018000
FLASH_BV_PRG =   0x0101A000

EBI_READ    = 4
EBI_WRITE   = 2

ebi_memory_map_items = {
        EBI_OFF_CSR0:("Chip Select Register 0", "EBI_CSR0", EBI_READ|EBI_WRITE,0x0000203e),
        EBI_OFF_CSR1:("Chip Select Register 1", "EBI_CSR1", EBI_READ|EBI_WRITE,0x10000000),
        EBI_OFF_CSR2:("Chip Select Register 2", "EBI_CSR2", EBI_READ|EBI_WRITE,0x20000000),
        EBI_OFF_CSR3:("Chip Select Register 3", "EBI_CSR3", EBI_READ|EBI_WRITE,0x30000000),
        EBI_OFF_CSR4:("Chip Select Register 4", "EBI_CSR4", EBI_READ|EBI_WRITE,0x40000000),
        EBI_OFF_CSR5:("Chip Select Register 5", "EBI_CSR5", EBI_READ|EBI_WRITE,0x50000000),
        EBI_OFF_CSR6:("Chip Select Register 6", "EBI_CSR6", EBI_READ|EBI_WRITE,0x60000000),
        EBI_OFF_CSR7:("Chip Select Register 7", "EBI_CSR7", EBI_READ|EBI_WRITE,0x70000000),
        EBI_OFF_MCR: ("Memory Control Register","EBI_MCR",  EBI_READ|EBI_WRITE,0),
        }

def ebi_csr_decode(reg):
    addr = reg>>20
    csen = (reg>>13)&1
    bat =  (reg>>12)&1
    tdf =  (reg>>9)&7
    pages =(reg>>7)&3
    wse =  (reg>>5)&1
    nws =  (reg>>2)&7
    dbw =  (reg&3)
    output = ["Base Address: %s"%hex(addr),
            "Chip Select: %s"%("False","True")[csen],
            "Byte Access Type: %s"%("Byte-Write","Byte-Access")[bat],
            "Data Float Output Time: %d cycles added"%tdf,
            "Page Size: %d MB"%(1,4,16,64)[pages],
            "Wait State: %s"%("disabled","enabled")[wse],
            "Wait States: %d"%nws,
            "Data Bus Size: %d bits"%dbw,
            ]
    return "\n".join(output)

mcr_ale = {
        0: ("A20,A21,A22,A23", 16, "None", "EBI_ALE_16M"),
        1: ("A20,A21,A22,A23", 16, "None", "EBI_ALE_16M"),
        2: ("A20,A21,A22,A23", 16, "None", "EBI_ALE_16M"),
        3: ("A20,A21,A22,A23", 16, "None", "EBI_ALE_16M"),
        4: ("A20,A21,A22", 8, "CS4", "EBI_ALE_8M"),
        5: ("A20,A21", 4, "CS4,CS5", "EBI_ALE_4M"),
        6: ("A20", 2, "CS4,CS5,CS6", "EBI_ALE_2M"),
        7: ("None", 1, "CS4,CS5,CS6,CS7", "EBI_ALE_1M"),
        }

def mcr_decode(mcr):
    validAddrBits,maxAddrSpace,validCS,codeLabel = mcr_decode[mcr&7]
    drp = mcr>>4
    output = ["Valid Address Bits: %s"%validAddrBits,
            "Maximum Address Space: %xMB"%maxAddrSpace,
            "Valid Chip Select: %s"%validCS,
            "Code Label:  %s"%codeLabel,
            ("Standard Read Protocol for all external memory devices enabled (EBI_DRP_STANDARD)","Early Read Protocol for all external memory devices enabled (EBI_DRP_EARLY)")[drp]
            ]
    return "\n".join(output)

def wd_omr_decode(omr):
    return "\n".join(["External Signal: %s"%("disabled","enabled")[(omr>>3)&1],
            "External Signal: %s"%("disabled","enabled")[(omr>>3)&1],
            "Interrupt: %s"%("disabled","enabled")[(omr>>2)&1],
            "Reset: %s"%("disabled","enabled")[(omr>>1)&1],
            "Watch Dog: %s"%("disabled","enabled")[(omr)&1],
            ])
def wd_cmr_decode(cmr):
    return "MCK/%d"%(8,32,128,1024)[(cmr>>2)&0xf]





class GoodFETAT91X40(GoodFETARM):
    def getChipSelectReg(self, chipnum):
        addr = EBI_BASE + (chipnum*4)
        reg, = self.ARMreadMem(addr,1)
        return reg
    def getChipSelectRegstr(self, chipnum):
        return ebi_csr_decode(self.getChipSelectReg(chipnum))

    def getEBIMemoryMap(self):
        keys = ebi_memory_map_items.keys()
        keys.sort()
        output = [ "EBI Memory Map"]
        for x in xrange(8):
            desc,name,rw,default = ebi_memory_map_items[x*4]
            output.append("\nMAP: %s (%s) - default: %x\n%s"%(name,desc,default,self.getChipSelectRegstr(x)))
        return "\n".join(output)
    def getMemoryControlRegister(self):
        mcr = self.ARMreadMem(EBI_MCR)
        return mcr
    def getMemoryControlRegisterstr(self):
        return mcr_decode(self.getMemoryControlRegister())

    def getInterruptSourceModeReg(self, regnum):
        regval = self.ARMreadMem(AIC_SMR[regnum][0])
        return retval
    def getInterruptSourceModeRegstr(self, regnum):
        return aic_smr_decode(self.getInterruptSourceModeReg(regnum))
    def setInterruptSourceModeReg(self, regnum, val):
        self.ARMwriteMem(AIC_SMR[regnum][0], val)

    def getInterruptSourceVectorReg(self, regnum):
        regval = self.ARMreadMem(AIC_SVR[regnum][0])
        return retval
    def setInterruptSourceModeReg(self, regnum, val):
        self.ARMwriteMem(AIC_SVR[regnum][0], val)

    def getIRQVectorReg(self):
        return self.ARMreadMem(AIC_IVR)
    def getFIQVectorReg(self):
        return self.ARMreadMem(AIC_FVR)

    def getInterruptStatusReg(self):
        return self.ARMreadMem(AIC_ISR)
    def getInterruptPendingReg(self):
        return self.ARMreadMem(AIC_FSR)
    def getInterruptMaskReg(self):
        return self.ARMreadMem(AIC_IMR)
    def getCoreInterruptStatusReg(self):
        return self.ARMreadMem(AIC_CISR)
    def enableInterrupt(self, interrupt):
        self.ARMwriteMem(AIC_IECR, 1<<interrupt)
    def disableInterrupt(self, interrupt):
        self.ARMwriteMem(AIC_IDCR, 1<<interrupt)
    def setInterruptCommandReg(self, interrupt):
        self.ARMwriteMem(AIC_ISCR, 1<<interrupt)
    def clearInterruptCommandReg(self, interrupt):
        self.ARMwriteMem(AIC_ICCR, 1<<interrupt)
    def clearCurrentInterrupt(self):
        self.ARMwriteMem(AIC_EOICR, 1<<interrupt)
    def getSpuriousVectorReg(self):
        return self.ARMreadMem(AIC_SPU)
    def setSpuriousVectorReg(self, val):
        return self.ARMreadMem(AIC_SPU)

    def enablePIOpin(self, mask):
        self.ARMwriteMem(PIO_PER, mask)
    def disablePIOpin(self, mask):
        self.ARMwriteMem(PIO_PDR, mask)
    def getPIOstatus(self):
        return self.ARMreadMem(PIO_PSR)
    def enablePIOoutput(self,mask):
        self.ARMwriteMem(PIO_OER, mask)
    def disablePIOoutput(self,mask):
        self.ARMwriteMem(PIO_ODR, mask)
    def getPIOoutputStatus(self):
        return self.ARMreadMem(PIO_OSR)

    def setOutputPin(self,mask):
        self.ARMwriteMem(PIO_SODR, mask)
    def clearOutputPin(self,mask):
        self.ARMwriteMem(PIO_CODR, mask)
    def getOutputDataStatusReg(self):
        return self.ARMreadMem(PIO_ODSR)
    def getPinDataStatusReg(self):
        return self.ARMreadMem(PIO_PDSR)
    def enablePIOinterrupt(self, mask):
        self.ARMwriteMem(PIO_IER, mask)
    def disablePIOinterrupt(self, mask):
        self.ARMwriteMem(PIO_IDR, mask)
    def getPIOinterruptMaskReg(self):
        return self.ARMreadMem(PIO_IMR)
    def getPIOinteruptStatusReg(self):
        return self.ARMreadMem(PIO_ODSR)


    def getWatchDogOverflowModeReg(self):
        return self.ARMreadMem(WD_OMR)
    def getWatchDogOverflowModeStr(self):
        return wd_omr_decode(self.getWatchDogOverflowModeReg())
    def setWatchDogOverflowModeReg(self, mode=0x2340):
        self.ARMwriteMem(WD_OMR, mode)
    def getWatchDogClockModeReg(self):
        return self.ARMreadMem(WD_CMR)
    def setWatchDogClockModeReg(self, mode=0x06e):
        self.ARMwriteMem(WD_CMR, mode)
    def setWatchDogControlReg(self, mode=0xC071):
        self.ARMwriteMem(WD_CR, mode)
    def getWatchDogStatusReg(self):
        return self.ARMreadMem(WD_SR)

    def getChipID(self):
        chipid = self.ARMreadMem(SF_CIDR,1)
        return chipid[0]
    def getResetStatusReg(self):
        return self.ARMreadMem(SF_RSR)
    def getMemoryModeReg(self):
        return self.ARMreadMem(SF_MMR)
    def setMemoryModeReg(self, val=0):
        self.ARMwriteMem(SF_MMR, val)
    def getProtectModeReg(self):
        return self.ARMreadMem(SF_PMR)
    def setProtectModeReg(self, val=0x27a80000):
        self.ARMwriteMem(SF_PMR, val)







    def ARMwriteFirmware(self, firmware):
        self.halt()
        chipid = self.ARMgetChipID()
        # FIXME: initialize PLL or EBI
        self.ARMmassErase(chipid)
        self.ARMset_regCPSR(PM_svc)   # set supervisor mode
        # FIXME: download the "flash identifier" program into target RAM
        self.ARMsetPC(PROGGYBASE)
        self.release()
        # get manufacturer crap through DCC (really??  screw this...)
        self.halt()
        if (self.ARMget_regCPSR() & PM_svc != PM_svc):
            raise Exception("No longer in Supervisor mode after firmware upload")
        # FIXME: download the downloader program into target RAM
        self.ARMsetPC(PROGGYBASE)
        self.release()
        # FIXME: use DCC to upload the new firmware
