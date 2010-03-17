/*! \file jtagarm7tdmi.c
  \author Matthew Carpenter <matt@inguardians.com>
  \brief ARM7TDMI JTAG (AT91R40008)
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"
#include "jtagarm7tdmi.h"


/**** 20-pin Connection Information (pin1 is on top-right for both connectors)****
GoodFET  ->  7TDMI 20-pin connector (HE-10 connector)
  1               13 (TDO)
  2               1  (Vdd)
  3               5  (TDI)
  5               7  (TMS)
  7               9  (TCK)
  8               15 (nRST)
  9               4,6,8,10,12,14,16,18,20 (GND)
  11              17/3 (nTRST)  (different sources suggest 17 or 3 alternately)
********************************/

/**** 14-pin Connection Information (pin1 is on top-right for both connectors)****
GoodFET  ->  7TDMI 14-pin connector
  1               11 (TDO)
  2               1  (Vdd)
  3               5  (TDI)
  5               7  (TMS)
  7               9  (TCK)
  8               12 (nRST)
  9               2,4,6,8,10,14 (GND)
  11              3 (nTRST)

http://hri.sourceforge.net/tools/jtag_faq_org.html
********************************/

/****************************************************************
Enabling jtag likely differs with most platforms.  We will attempt to enable most from here.  Override jtagarm7tdmi_start() to extend for other implementations
ARM7TDMI enables three different scan chains:
    * Chain0 - "entire periphery" including data bus
    * Chain1 - core data bus (subset of Chain0)  - Instruction Pipeline
    * Chain2 - EmbeddedICE Logic Registers - This is our way into the fun stuff.
    

---
You can disable EmbeddedICE-RT by setting the DBGEN input LOW.
Caution
Hard wiring the DBGEN input LOW permanently disables all debug functionality.
When DBGEN is LOW, it inhibits DBGDEWPT, DBGIEBKPT, and EDBGRQ to
the core, and DBGACK from the ARM9E-S core is always LOW.
---


---
When the ARM9E-S core is in debug state, you can examine the core and system state
by forcing the load and store multiples into the instruction pipeline.
Before you can examine the core and system state, the debugger must determine
whether the processor entered debug from Thumb state or ARM state, by examining
bit 4 of the EmbeddedICE-RT debug status register. If bit 4 is HIGH, the core has
entered debug from Thumb state.
For more details about determining the core state, see Determining the core and system
state on page B-18.
---


--- olimex - http://www.olimex.com/dev/pdf/arm-jtag.pdf
JTAG signals description:
PIN.1 (VTREF) Target voltage sense. Used to indicate the target’s operating voltage to thedebug tool.
PIN.2 (VTARGET) Target voltage. May be used to supply power to the debug tool.
PIN.3 (nTRST) JTAG TAP reset, this signal should be pulled up to Vcc in target board.
PIN4,6, 8, 10,12,14,16,18,20 Ground. The Gnd-Signal-Gnd-Signal strategy implemented on the 20-way connection scheme improves noiseimmunity on the target connect cable.
*PIN.5 (TDI) JTAG serial data in, should be pulled up to Vcc on target board.
*PIN.7 (TMS) JTAG TAP Mode Select, should be pulled up to Vcc on target board.
*PIN.9 (TCK) JTAG clock.
PIN.11 (RTCK) JTAG retimed clock.Implemented on certain ASIC ARM implementations the host ASIC may need to synchronize external inputs (such as JTAG inputs) with its own internal clock.
*PIN.13 (TDO) JTAG serial data out.
*PIN.15 (nSRST) Target system reset.
*PIN.17 (DBGRQ) Asynchronous debug request.  DBGRQ allows an external signal to force the ARM core into debug mode, should be pull down to GND.
PIN.19 (DBGACK) Debug acknowledge. The ARM core acknowledges debug-mode inresponse to a DBGRQ input.

****************************************************************/


/************************** JTAGARM7TDMI Primitives ****************************/
void jtag_goto_shift_ir() {
  SETTMS;
  jtag_arm_tcktock();
  jtag_arm_tcktock();
  CLRTMS;
  jtag_arm_tcktock();
  jtag_arm_tcktock();

}

void jtag_goto_shift_dr() {
  SETTMS;
  jtag_arm_tcktock();
  CLRTMS;
  jtag_arm_tcktock();
  jtag_arm_tcktock();
}

void jtag_reset_to_runtest_idle() {
  SETTMS;
  jtag_arm_tcktock();
  jtag_arm_tcktock();
  jtag_arm_tcktock();
  jtag_arm_tcktock();
  jtag_arm_tcktock();  // now in Reset state
  CLRTMS;
  jtag_arm_tcktock();  // now in Run-Test/Idle state
}

void jtag_arm_tcktock() {
  CLRTCK; 
  //PLEDOUT^=PLEDPIN; 
  SETTCK; 
  //PLEDOUT^=PLEDPIN;
}

// ! Start JTAG, setup pins, reset TAP and return IDCODE
unsigned long jtagarm7tdmi_start() {
  debugstr("_start");
  jtagsetup();
  //Known-good starting position.
  //Might be unnecessary.
  SETTST;
  SETRST;
  
  delay(0xFF);
  
  //Entry sequence from Page 67 of SLAU265A for 4-wire JTAG
  CLRRST;
  delay(20);
  CLRTST;

  msdelay(10);
  SETRST;
  /*
  P5DIR &=~RST;
  */
  delay(0xFF);
  jtagarm7tdmi_resettap();
  return jtagarm7tdmi_idcode();
}


//! Reset TAP State Machine       
void jtagarm7tdmi_resettap(){               // PROVEN
  current_chain = -1;
  jtag_reset_to_runtest_idle();
}


//  NOTE: important: THIS MODULE REVOLVES AROUND RETURNING TO RUNTEST/IDLE, OR THE FUNCTIONAL EQUIVALENT


//! Shift N bits over TDI/TDO.  May choose LSB or MSB, and select whether to terminate (TMS-high on last bit) and whether to return to RUNTEST/IDLE
unsigned long jtagarmtransn(unsigned long word, unsigned char bitcount, unsigned char lsb, unsigned char end, unsigned char retidle){               // PROVEN
  unsigned int bit;
  unsigned long high = 1;
  unsigned long mask;
  debugstr("_transn");

  for (bit=(bitcount-1)/16; bit>0; bit--)
    high <<= 16;
  high <<= ((bitcount-1)%16);

  mask = high-1;

  if (lsb) {
    for (bit = bitcount; bit > 0; bit--) {
      /* write MOSI on trailing edge of previous clock */
      if (word & 1)
        {SETMOSI;}
      else
        {CLRMOSI;}
      word >>= 1;

      if (bit==1 && end)
        SETTMS;//TMS high on last bit to exit.
       
      jtag_arm_tcktock();

      /* read MISO on trailing edge */
      if (READMISO){
        word += (high);
      }
    }
  } else {
    for (bit=bitcount; bit>0; bit++) {
      /* write MOSI on trailing edge of previous clock */
      if (word & high)
        {SETMOSI;}
      else
        {CLRMOSI;}
      word = (word & mask) << 1;

      if (bit==1 && end)
        SETTMS;//TMS high on last bit to exit.

      jtag_arm_tcktock();

      /* read MISO on trailing edge */
      word |= READMISO;
    }
  }

  if (end){
    // exit state
    jtag_arm_tcktock();
    // update state
    if (retidle){
      CLRTMS;
      jtag_arm_tcktock();
    }
  }
  return word;
}



/************************************************************************
* ARM7TDMI core has 6 primary registers to be connected between TDI/TDO
*   * Bypass Register
*   * ID Code Register
*   * Scan Chain Select Register    (4 bits_lsb)
*   * Scan Chain 0                  (64+* bits: 32_databits_lsb + ctrlbits + 32_addrbits_msb)
*   * Scan Chain 1                  (33 bits: 32_bits + BREAKPT)
*   * Scan Chain 2                  (38 bits: rw + 5_regbits_msb + 32_databits_msb)
************************************************************************/



/************************** Basic JTAG Verb Commands *******************************/
//! Grab the core ID.
unsigned long jtagarm7tdmi_idcode(){               // PROVEN
  jtagarm7tdmi_resettap();
  SHIFT_IR;
  jtagarmtransn(ARM7TDMI_IR_IDCODE, 4, LSB, END, RETIDLE);
  SHIFT_DR;
  return jtagarmtransn(0,32, LSB, END, RETIDLE);
}

//!  Connect Bypass Register to TDO/TDI
unsigned char jtagarm7tdmi_bypass(){               // PROVEN
  jtagarm7tdmi_resettap();
  SHIFT_IR;
  return jtagarmtransn(ARM7TDMI_IR_BYPASS, 4, LSB, END, NORETIDLE);
}
//!  INTEST verb - do internal test
unsigned char jtagarm7tdmi_intest() { 
  jtagarm7tdmi_resettap();
  SHIFT_IR;
  return jtagarmtransn(ARM7TDMI_IR_INTEST, 4, LSB, END, NORETIDLE); 
}

//!  EXTEST verb
unsigned char jtagarm7tdmi_extest() { 
  jtagarm7tdmi_resettap();
  SHIFT_IR;
  return jtagarmtransn(ARM7TDMI_IR_EXTEST, 4, LSB, END, NORETIDLE);
}

//!  SAMPLE verb
//unsigned long jtagarm7tdmi_sample() { 
//  debugstr("_sample");
//  jtagarm7tdmi_ir_shift4(ARM7TDMI_IR_SAMPLE);        // ???? same here.
//  return jtagtransn(0,32);
//}

//!  RESTART verb
unsigned char jtagarm7tdmi_restart() { 
  jtagarm7tdmi_resettap();
  SHIFT_IR;
  return jtagarmtransn(ARM7TDMI_IR_RESTART, 4, LSB, END, RETIDLE); 
}

//!  ARM7TDMI_IR_CLAMP               0x5
unsigned long jtagarm7tdmi_clamp() { 
  jtagarm7tdmi_resettap();
  SHIFT_IR;
  jtagarmtransn(ARM7TDMI_IR_CLAMP, 4, LSB, END, NORETIDLE);
  SHIFT_DR;
  return jtagarmtransn(0, 32, LSB, END, RETIDLE);
}

//!  ARM7TDMI_IR_HIGHZ               0x7
unsigned char jtagarm7tdmi_highz() { 
  jtagarm7tdmi_resettap();
  SHIFT_IR;
  return jtagarmtransn(ARM7TDMI_IR_HIGHZ, 4, LSB, END, NORETIDLE);
}

//! define ARM7TDMI_IR_CLAMPZ              0x9
unsigned char jtagarm7tdmi_clampz() { 
  jtagarm7tdmi_resettap();
  SHIFT_IR;
  return jtagarmtransn(ARM7TDMI_IR_CLAMPZ, 4, LSB, END, NORETIDLE);
}


//!  Connect the appropriate scan chain to TDO/TDI.  SCAN_N, INTEST, ENDS IN SHIFT_DR!!!!!
unsigned long jtagarm7tdmi_scan(int chain, int testmode) {               // PROVEN
  debugstr("_scan");
/*
When selecting a scan chain the “Run Test/Idle” state should never be reached, other-
wise, when in debug state, the core will not be correctly isolated and intrusive
commands occur. Therefore, it is recommended to pass directly from the “Update”
state” to the “Select DR” state each time the “Update” state is reached.
*/
  unsigned long retval;
  if (current_chain != chain) {     // breaks shit when going from idcode back to scan chain
    SHIFT_IR;
    jtagarmtransn(ARM7TDMI_IR_SCAN_N, 4, LSB, END, NORETIDLE);
    SHIFT_DR;
    retval = jtagarmtransn(chain, 4, LSB, END, NORETIDLE);
    current_chain = chain;
  }    else
    retval = current_chain;
  // put in test mode...
  SHIFT_IR;
  jtagarmtransn(testmode, 4, LSB, END, RETIDLE); 

  current_chain = chain;

  return(retval);
}


//!  Connect the appropriate scan chain to TDO/TDI.  SCAN_N, INTEST, ENDS IN SHIFT_DR!!!!!
unsigned long jtagarm7tdmi_scan_intest(int chain) {               // PROVEN
  return jtagarm7tdmi_scan(chain, ARM7TDMI_IR_INTEST);
}




//! push an instruction into the pipeline  - Assumes scan-chain 1 is already INTEST
unsigned long jtagarm7tdmi_instr_primitive(unsigned long instr, char breakpt){
  unsigned long retval;
  jtagarm7tdmi_scan_intest(1);
  SHIFT_DR;
  // if the next instruction is to run using MCLK (master clock), set TDI
  if (breakpt)
    {
    SETMOSI;
    count_sysspd_instr_since_debug++;
    } 
  else
    {
    CLRMOSI; 
    count_dbgspd_instr_since_debug++;
    }

  jtag_arm_tcktock();
  
  // Now shift in the 32 bits
  retval = jtagarmtransn(instr, 32, MSB, END, RETIDLE);    // Must return to RUN-TEST/IDLE state for instruction to enter pipeline, and causes debug clock.
  //jtag_arm_tcktock();
  return(retval);
  
}


unsigned long jtagarm7tdmi_nop(char breakpt){
  return jtagarm7tdmi_instr_primitive(ARM_INSTR_NOP, breakpt);
}

/*    stolen from ARM DDI0029G documentation, translated using ARM Architecture Reference Manual (14128.pdf)
STR R0, [R0]; Save R0 before use
MOV R0, PC ; Copy PC into R0
STR R0, [R0]; Now save the PC in R0
BX PC ; Jump into ARM state
MOV R8, R8 ;
MOV R8, R8 ;
NOP
NOP

*/
//! set the current mode to ARM, returns PC (FIXME).  Should be used by haltcpu(), which should also store PC and the THUMB state, for use by releasecpu();
unsigned long jtagarm7tdmi_setMode_ARM(){               // PROVEN
  unsigned long retval = 0xff;
  while ((jtagarm7tdmi_get_dbgstate() & JTAG_ARM7TDMI_DBG_TBIT)&& retval-- > 0){
    jtagarm7tdmi_scan_intest(1);
    cmddataword[6] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_NOP,0);
    cmddataword[1] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_STR_R0_r0,0);
    cmddataword[2] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_MOV_R0_PC,0);
    cmddataword[3] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_STR_R0_r0,0);
    cmddataword[4] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_BX_PC,0);
    cmddataword[5] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_NOP,0);
    cmddataword[6] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_NOP,0);
    delay(10);
  }
  return(retval);
}




/************************* EmbeddedICE Primitives ****************************/
//! shifter for writing to chain2 (EmbeddedICE). 
unsigned long eice_write(unsigned char reg, unsigned long data){
  unsigned long retval, temp;
  jtagarm7tdmi_scan_intest(2);
  // Now shift in the 32 bits
  SHIFT_DR;
  retval = jtagarmtransn(data, 32, LSB, NOEND, NORETIDLE);          // send in the data - 32-bits lsb
  temp = jtagarmtransn(reg, 5, LSB, NOEND, NORETIDLE);              // send in the register address - 5 bits lsb
  jtagarmtransn(1, 1, LSB, END, RETIDLE);              // send in the register address - 5 bits lsb
  
  //SETTMS;   // Last Bit - Exit UPDATE_DR
  //// is this update a read/write or just read?
  //SETMOSI;
  //jtag_arm_tcktock();
  
  return(retval); 
}

//! shifter for reading from chain2 (EmbeddedICE).
unsigned long eice_read(unsigned char reg){               // PROVEN
  unsigned long temp;
  jtagarm7tdmi_scan_intest(2);

  // send in the register address - 5 bits LSB
  SHIFT_DR;
  temp = jtagarmtransn(reg, 5, LSB, NOEND, NORETIDLE);
  
  // clear TDI to select "read only"
  jtagarmtransn(0, 1, LSB, END, RETIDLE);
  
  SHIFT_DR;
  // Now shift out the 32 bits
  return(jtagarmtransn(0, 32, LSB, END, RETIDLE));   // atmel arm jtag docs pp.10-11: LSB first
  
}




/************************* ICEBreaker/EmbeddedICE Stuff ******************************/
//! Grab debug register
unsigned long jtagarm7tdmi_get_dbgstate() {       // ICE Debug register, *NOT* ARM register DSCR    //    PROVEN
  return eice_read(EICE_DBGSTATUS);
}

//! Grab debug register
unsigned long jtagarm7tdmi_get_dbgctrl() {
  return eice_read(EICE_DBGCTRL);
}

//! Update debug register
unsigned long jtagarm7tdmi_set_dbgctrl(unsigned long bits) {
  return eice_write(EICE_DBGCTRL, bits);
}



//!  Set and Enable Watchpoint 0
void jtagarm7tdmi_set_watchpoint0(unsigned long addr, unsigned long addrmask, unsigned long data, unsigned long datamask, unsigned long ctrl, unsigned long ctrlmask){
  // store watchpoint info?  - not right now
    // FIXME: store info

  // write 0 in watchpoint 0 address
  eice_write(EICE_WP0ADDR, addr);
  // write 0xffffffff in watchpoint 0 address mask
  eice_write(EICE_WP0ADDRMASK, addrmask);
  // write 0 in watchpoint 0 data
  eice_write(EICE_WP0DATA, data);
  // write 0xffffffff in watchpoint 0 data mask
  eice_write(EICE_WP0DATAMASK, datamask);
  // write 0x00000100 in watchpoint 0 control value register (enables watchpoint)
  eice_write(EICE_WP0CTRL, ctrlmask);
  // write 0xfffffff7 in watchpoint 0 control mask - only detect the fetch instruction
  eice_write(EICE_WP0CTRLMASK, ctrlmask);
}

//!  Set and Enable Watchpoint 1
void jtagarm7tdmi_set_watchpoint1(unsigned long addr, unsigned long addrmask, unsigned long data, unsigned long datamask, unsigned long ctrl, unsigned long ctrlmask){
  // store watchpoint info?  - not right now
    // FIXME: store info

  // write 0 in watchpoint 1 address
  eice_write(EICE_WP1ADDR, addr);
  // write 0xffffffff in watchpoint 1 address mask
  eice_write(EICE_WP1ADDRMASK, addrmask);
  // write 0 in watchpoint 1 data
  eice_write(EICE_WP1DATA, data);
  // write 0xffffffff in watchpoint 1 data mask
  eice_write(EICE_WP1DATAMASK, datamask);
  // write 0x00000100 in watchpoint 1 control value register (enables watchpoint)
  eice_write(EICE_WP1CTRL, ctrl);
  // write 0xfffffff7 in watchpoint 1 control mask - only detect the fetch instruction
  eice_write(EICE_WP1CTRLMASK, ctrlmask);
}

//!  Disable Watchpoint 0
void jtagarm7tdmi_disable_watchpoint0(){
  // write 0 in watchpoint 0 control value - disables watchpoint 0
  eice_write(EICE_WP0CTRL, 0x0);
}
  
//!  Disable Watchpoint 1
void jtagarm7tdmi_disable_watchpoint1(){
  // write 0 in watchpoint 0 control value - disables watchpoint 0
  eice_write(EICE_WP1CTRL, 0x0);
}



/******************** Complex Commands **************************/
//! Push an instruction into the CPU pipeline
//  NOTE!  Must provide EXECNOPARM for parameter if no parm is required.
unsigned long test_exec(unsigned long instr, unsigned long parameter, unsigned char systemspeed) {
  unsigned long retval;

  cmddatalong[1] = jtagarm7tdmi_nop( 0);
  cmddatalong[2] = jtagarm7tdmi_nop(systemspeed);
  // write 32-bit instruction code into DR
  cmddatalong[3] = jtagarm7tdmi_instr_primitive(instr, 0);
  cmddatalong[4] = jtagarm7tdmi_nop( 0);
  cmddatalong[5] = jtagarm7tdmi_nop( 0);
  // inject long
  cmddatalong[6] = jtagarm7tdmi_instr_primitive(parameter, 0);
  cmddatalong[7] = jtagarm7tdmi_nop( 0);
  cmddatalong[8] = jtagarm7tdmi_nop( 0);
  cmddatalong[9] = jtagarm7tdmi_nop( 0);
  retval = cmddatalong[9];

  return(retval);
}


//! Push an instruction into the CPU pipeline
//  NOTE!  Must provide EXECNOPARM for parameter if no parm is required.
unsigned long jtagarm7tdmi_exec(unsigned long instr, unsigned long parameter, unsigned char systemspeed) {
  unsigned long retval;

  cmddatalong[1] = jtagarm7tdmi_nop( 0);
  cmddatalong[2] = jtagarm7tdmi_nop(systemspeed);
  // write 32-bit instruction code into DR
  cmddatalong[3] = jtagarm7tdmi_instr_primitive(instr, 0);
  cmddatalong[4] = jtagarm7tdmi_nop( 0);
  cmddatalong[5] = jtagarm7tdmi_nop( 0);
  // inject long
  cmddatalong[6] = jtagarm7tdmi_instr_primitive(parameter, 0);
  cmddatalong[7] = jtagarm7tdmi_nop( 0);
  retval = jtagarm7tdmi_nop( 0);
  cmddatalong[9] = jtagarm7tdmi_nop( 0);
  cmddatalong[8] = retval;

  return(retval);
}

//! Retrieve a 32-bit Register value
unsigned long jtagarm7tdmi_get_register(unsigned char reg) {
  unsigned long retval = 0, instr;
  // push nop into pipeline - clean out the pipeline...
  cmddatalong[2] = jtagarm7tdmi_nop( 0);

  // push STR_Rx, [R14] into pipeline
  instr = ARM_INSTR_STR_Rx_r14 + ((reg<<12)&0xf00);
  cmddatalong[1] = jtagarm7tdmi_instr_primitive(instr, 0);
  // push nop into pipeline - fetched
  cmddatalong[2] = jtagarm7tdmi_nop( 0);
  // push nop into pipeline - decoded
  cmddatalong[3] = jtagarm7tdmi_nop( 0);
  // push nop into pipeline - executed 
  cmddatalong[4] = jtagarm7tdmi_nop( 0);
  // recover 32-bit word
  //retval = jtagarmtransn(0, 32, LSB, END, RETIDLE);
  retval = jtagarm7tdmi_nop( 0);
  cmddatalong[5] = retval;
  cmddatalong[6] = jtagarm7tdmi_nop( 0);
  cmddatalong[7] = jtagarm7tdmi_nop( 0);
  cmddatalong[8] = jtagarm7tdmi_nop( 0);
  return retval;
}

//! Set a 32-bit Register value
unsigned long jtagarm7tdmi_set_register(unsigned char reg, unsigned long val) {
  unsigned long retval = 0, instr;
  // push nop into pipeline - clean out the pipeline...
  cmddatalong[2] = jtagarm7tdmi_nop( 0);

  // push STR_Rx, [R14] into pipeline
  instr = ARM_INSTR_LDR_Rx_r14 + ((reg<<12)&0xf00);
  cmddatalong[1] = jtagarm7tdmi_instr_primitive(instr, 0);
  // push nop into pipeline - fetched
  cmddatalong[2] = jtagarm7tdmi_nop( 0);
  // push nop into pipeline - decoded
  cmddatalong[2] = jtagarm7tdmi_nop( 0);
  
  // push 32-bit word on data bus - execute state
  //retval = jtagarmtransn(val, 32, LSB, END, RETIDLE);
  cmddatalong[3] = jtagarm7tdmi_instr_primitive(val, 0);
  // push nop into pipeline - executed 
  cmddatalong[4] = jtagarm7tdmi_nop( 0);
  if (reg == ARM_REG_PC){
    cmddatalong[5] = jtagarm7tdmi_nop( 0);
    cmddatalong[6] = jtagarm7tdmi_nop( 0);
  }
  retval = jtagarm7tdmi_nop( 0);
  cmddatalong[7] = retval;
  return(retval);
}



//! Get all registers.  Return an array
unsigned long* jtagarm7tdmi_get_registers() {
  cmddatalong[1] = jtagarm7tdmi_instr_primitive(ARM_INSTR_SKANKREGS,0);
  cmddatalong[2] = jtagarm7tdmi_nop( 0);
  cmddatalong[3] = jtagarm7tdmi_nop( 0);
  cmddatalong[4] = jtagarm7tdmi_nop( 0);
  cmddatalong[5] = jtagarm7tdmi_nop( 0);
  cmddatalong[6] = jtagarm7tdmi_nop( 0);
  cmddatalong[7] = jtagarm7tdmi_nop( 0);
  cmddatalong[8] = jtagarm7tdmi_nop( 0);
  cmddatalong[9] = jtagarm7tdmi_nop( 0);
  cmddatalong[10] = jtagarm7tdmi_nop( 0);
  cmddatalong[11] = jtagarm7tdmi_nop( 0);
  cmddatalong[12] = jtagarm7tdmi_nop( 0);
  cmddatalong[13] = jtagarm7tdmi_nop( 0);
  cmddatalong[14] = jtagarm7tdmi_nop( 0);
  cmddatalong[15] = jtagarm7tdmi_nop( 0);
  cmddatalong[16] = jtagarm7tdmi_nop( 0);
  cmddatalong[17] = jtagarm7tdmi_nop( 0);
  cmddatalong[18] = jtagarm7tdmi_nop( 0);
  cmddatalong[19] = jtagarm7tdmi_nop( 0);
  cmddatalong[20] = jtagarm7tdmi_nop( 0);
  return registers;
}

//! Retrieve the CPSR Register value
unsigned long jtagarm7tdmi_get_regCPSR() {
  unsigned long retval = 0;

  // push nop into pipeline - clean out the pipeline...
  cmddatalong[1] = jtagarm7tdmi_nop( 0);
  // push MRS_R0, CPSR into pipeline
  cmddatalong[1] = jtagarm7tdmi_instr_primitive(ARM_INSTR_MRS_R0_CPSR, 0);
  // push nop into pipeline - fetched
  cmddatalong[3] = jtagarm7tdmi_nop( 0);
  // push nop into pipeline - decoded
  cmddatalong[4] = jtagarm7tdmi_nop( 0);
  // push nop into pipeline - executed 
  cmddatalong[5] = jtagarm7tdmi_nop( 0);
  // recover 32-bit word
  retval = jtagarm7tdmi_nop( 0);
  cmddatalong[5] = retval;
  return retval;
}

//! Retrieve the CPSR Register value
unsigned long jtagarm7tdmi_set_regCPSR(unsigned long val) {
  unsigned long retval = 0;

  // push nop into pipeline - clean out the pipeline...
  cmddatalong[1] = jtagarm7tdmi_nop( 0);
  // push MSR cpsr_cxsf, R0 into pipeline
  cmddatalong[1] = jtagarm7tdmi_instr_primitive(ARM_INSTR_MSR_cpsr_cxsf_R0, 0);
  // push nop into pipeline - fetched
  cmddatalong[2] = jtagarm7tdmi_nop( 0);
  // push nop into pipeline - decoded
  cmddatalong[3] = jtagarm7tdmi_nop( 0);
  
  // push 32-bit word on data bus
  retval = jtagarm7tdmi_instr_primitive(val, 0);
  // push nop into pipeline - executed 
  cmddatalong[5] = jtagarm7tdmi_nop( 0);
  cmddatalong[4] = retval;
  return(retval);
}

//! Write data to address - Assume TAP in run-test/idle state
unsigned long jtagarm7tdmi_writemem(unsigned long adr, unsigned long data){
  unsigned long r0=0, r1=-1;

  // store R0 and R1
  r0 = jtagarm7tdmi_get_register(0);
  r1 = jtagarm7tdmi_get_register(1);
  // write address into R0
  jtagarm7tdmi_set_register(0, adr);
  // write data in R1
  jtagarm7tdmi_set_register(1, data);
  //retval = jtagarm7tdmi_exec(ARM_INSTR_LDR_R1_r0_4,1);
  // push nop into pipeline to "clean" it ???
  jtagarm7tdmi_nop( 0);
  // push nop into pipeline with BREAKPT set
  jtagarm7tdmi_nop( 1);
  // push LDR R1, R0, #4 into instruction pipeline
  jtagarm7tdmi_instr_primitive(ARM_INSTR_LDR_R1_r0_4, 0);
  // push nop into pipeline
  jtagarm7tdmi_nop( 0);
  // restore R0 and R1 
  jtagarm7tdmi_set_register(1, r1);
  jtagarm7tdmi_set_register(0, r0);
  return(-1);
}

//! Read data from address
unsigned long jtagarm7tdmi_readmem(unsigned long adr){
  unsigned long retval = 0;
  unsigned long r0=0, r1=-1;
  int waitcount = 0xfff;

  // select chain 2
  // store R0 and R1  - not yet...
  r0 = jtagarm7tdmi_get_register(0);
  r1 = jtagarm7tdmi_get_register(1);
  // write address into R0
  jtagarm7tdmi_set_register(0, adr);
  // push nop into pipeline to "clean" it ???
  jtagarm7tdmi_nop( 0);
  // push nop into pipeline with BREAKPT set
  jtagarm7tdmi_nop( 1);
  // push LDR R1, R0, #4 into instruction pipeline
  jtagarm7tdmi_instr_primitive(ARM_INSTR_LDR_R1_r0_4, 0);
  // push nop into pipeline
  jtagarm7tdmi_nop( 0);
  // SHIFT_IR with RESTART instruction
  jtagarm7tdmi_restart();
  // Poll the Debug Status Register for DBGACK and nMREQ to be HIGH
  while ((jtagarm7tdmi_get_dbgstate() & 1) == 0  && waitcount > 0){
    delay(1);
    waitcount --;
  }
  if (waitcount == 0xffff){
    return (-1);
  } else {
    retval = jtagarm7tdmi_get_register(1);
  // read memory value from R1 register
  // restore R0 and R1 
  jtagarm7tdmi_set_register(1, r1);
  jtagarm7tdmi_set_register(0, r0);
  }
  return retval;
}


//! Read Program Counter
unsigned long jtagarm7tdmi_getpc(){
  return jtagarm7tdmi_get_register(ARM_REG_PC);
}

//! Set Program Counter
unsigned long jtagarm7tdmi_setpc(unsigned long adr){
  return jtagarm7tdmi_set_register(ARM_REG_PC, adr);
}

//! Halt CPU - returns 0xffff if the operation fails to complete within 
unsigned long jtagarm7tdmi_haltcpu(){                   //  PROVEN
  int waitcount = 0xfff;

  // store watchpoint info?  - not right now
  // write 0 in watchpoint 1 address
  eice_write(EICE_WP1ADDR, 0);
  // write 0xffffffff in watchpoint 1 address mask
  eice_write(EICE_WP1ADDRMASK, 0xffffffff);
  // write 0 in watchpoint 1 data
  eice_write(EICE_WP1DATA, 0);
  // write 0xffffffff in watchpoint 1 data mask
  eice_write(EICE_WP1DATAMASK, 0xffffffff);
  // write 0x00000100 in watchpoint 1 control value register (enables watchpoint)
  eice_write(EICE_WP1CTRL, 0x100);                              //!!!!! WTF!  THIS IS SUPPOSED TO BE 9 bits wide?!?
  // write 0xfffffff7 in watchpoint 1 control mask - only detect the fetch instruction
  eice_write(EICE_WP1CTRLMASK, 0xfffffff7);                     //!!!!! WTF!  THIS IS SUPPOSED TO BE 8 bits wide?!?
  // poll until debug status says the cpu is in debug mode
  while (!(jtagarm7tdmi_get_dbgstate() & 0x1)   && waitcount > 0){
    delay(5);
    waitcount --;
  }
  // write 0 in watchpoint 0 control value - disables watchpoint 0
  eice_write(EICE_WP1CTRL, 0x0);

  // store the debug state
  last_halt_debug_state = jtagarm7tdmi_get_dbgstate();
  last_halt_pc = jtagarm7tdmi_getpc() - 4;   // assume -4 for entering debug mode via watchpoint.
  count_dbgspd_instr_since_debug = 0;
  count_sysspd_instr_since_debug = 0;
  if (last_halt_debug_state & JTAG_ARM7TDMI_DBG_TBIT){
    jtagarm7tdmi_setMode_ARM();
  }
  return waitcount;
}

unsigned long jtagarm7tdmi_releasecpu(){
  int waitcount = 0xfff;
  unsigned long instr;
  // somehow determine what PC should be (a couple ways possible, calculations required)
  // NOP
  jtagarm7tdmi_nop(0);
  // NOP/BREAKPT
  jtagarm7tdmi_nop(1);

  if (last_halt_debug_state & JTAG_ARM7TDMI_DBG_TBIT){
    instr = ARM_INSTR_BX_PC + 0x1000000 - (count_dbgspd_instr_since_debug) - (count_sysspd_instr_since_debug*3);  //FIXME: make this right  - can't we just do an a7solute b/bx?
    jtagarm7tdmi_instr_primitive(instr,0);
  } else {
    instr = ARM_INSTR_B_PC + 0x1000000 - (count_dbgspd_instr_since_debug) - (count_sysspd_instr_since_debug*3);  //FIXME: make this right  - can't we just do an absolute b/bx?
    jtagarm7tdmi_instr_primitive(instr,0);
  }
  // VERB_RESTART
  SHIFT_IR;
  jtagarmtransn(ARM7TDMI_IR_RESTART,4,LSB,END,RETIDLE);

  // wait until restart-bit set in debug state register
  while ((jtagarm7tdmi_get_dbgstate() & JTAG_ARM7TDMI_DBG_DBGACK) && waitcount > 0){
    //delay(1);
    waitcount --;
  }
  last_halt_debug_state = -1;
  last_halt_pc = -1;
  return 0;
}
 



///////////////////////////////////////////////////////////////////////////////////////////////////
//! Handles ARM7TDMI JTAG commands.  Forwards others to JTAG.
void jtagarm7tdmihandle(unsigned char app, unsigned char verb, unsigned long len){
  register char blocks;
  
  unsigned int i,val;
  unsigned long at;
  
  jtagarm7tdmi_resettap();
  debugstr("Classic ARM JTAG handler.");

  //PLEDOUT^=PLEDPIN; 
  switch(verb){
  case START:
    //Enter JTAG mode.
    cmddatalong[0] = jtagarm7tdmi_start();
    cmddatalong[1] = jtagarm7tdmi_haltcpu();
    //jtagarm7tdmi_resettap();
    txdata(app,verb,0x8);
    break;
  case JTAGARM7TDMI_READMEM:
  case PEEK:
    blocks=(len>4?cmddata[4]:1);
    at=cmddatalong[0];
    
    len=0x80;
    txhead(app,verb,len);
    
    while(blocks--){
      for(i=0;i<len;i+=2){
	jtagarm7tdmi_resettap();
	delay(10);
	
	val=jtagarm7tdmi_readmem(at);
		
	at+=2;
	serial_tx(val&0xFF);
	serial_tx((val&0xFF00)>>8);
      }
    }
    
    break;
  case JTAGARM7TDMI_GET_CHIP_ID:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_idcode();
    txdata(app,verb,4);
    PLEDOUT^=PLEDPIN; 
    break;


  case JTAGARM7TDMI_WRITEMEM:
  case POKE:
	jtagarm7tdmi_resettap();
    jtagarm7tdmi_writemem(cmddatalong[0],
		       cmddataword[2]);
    cmddataword[0]=jtagarm7tdmi_readmem(cmddatalong[0]);
    txdata(app,verb,2);
    break;

  case JTAGARM7TDMI_HALTCPU:  
    cmddatalong[0] = jtagarm7tdmi_haltcpu();
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_RELEASECPU:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_releasecpu();
    txdata(app,verb,4);
    break;
  //unimplemented functions
  //case JTAGARM7TDMI_SETINSTRFETCH:
  //case JTAGARM7TDMI_WRITEFLASH:
  //case JTAGARM7TDMI_ERASEFLASH:
  case JTAGARM7TDMI_SET_PC:
    cmddatalong[0] = jtagarm7tdmi_setpc(cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_GET_DEBUG_CTRL:
    cmddatalong[0] = jtagarm7tdmi_get_dbgctrl();
    txdata(app,verb,1);
    break;
  case JTAGARM7TDMI_SET_DEBUG_CTRL:
    cmddatalong[0] = jtagarm7tdmi_set_dbgctrl(cmddata[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_GET_PC:
    cmddatalong[0] = jtagarm7tdmi_getpc();
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_GET_DEBUG_STATE:
    //jtagarm7tdmi_resettap();            // Shouldn't need this, but currently do.  FIXME!
    cmddatalong[0] = jtagarm7tdmi_get_dbgstate();
    txdata(app,verb,4);
    break;
  //case JTAGARM7TDMI_GET_WATCHPOINT:
  //case JTAGARM7TDMI_SET_WATCHPOINT:
  case JTAGARM7TDMI_GET_REGISTER:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_get_register(cmddata[0]);
    txdata(app,verb,96);
    break;
  case JTAGARM7TDMI_SET_REGISTER:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = cmddatalong[1];
    jtagarm7tdmi_set_register(cmddata[0], cmddatalong[1]);
    txdata(app,verb,96);
    break;
  case JTAGARM7TDMI_GET_REGISTERS:
	jtagarm7tdmi_resettap();
    jtagarm7tdmi_get_registers();
    txdata(app,verb,80);
    break;
  //case JTAGARM7TDMI_SET_REGISTERS:
  case JTAGARM7TDMI_DEBUG_INSTR:
	jtagarm7tdmi_resettap();
    cmddataword[0] = jtagarm7tdmi_exec(cmddataword[0], cmddataword[1], cmddata[9]);
    txdata(app,verb,80);
    break;
  case JTAGARM7TDMI_STEP_INSTR:
/*  case JTAGARM7TDMI_READ_CODE_MEMORY:
  case JTAGARM7TDMI_WRITE_FLASH_PAGE:
  case JTAGARM7TDMI_READ_FLASH_PAGE:
  case JTAGARM7TDMI_MASS_ERASE_FLASH:
  case JTAGARM7TDMI_PROGRAM_FLASH:
  case JTAGARM7TDMI_LOCKCHIP:
  case JTAGARM7TDMI_CHIP_ERASE:
  */
// Really ARM specific stuff
  case JTAGARM7TDMI_GET_CPSR:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_get_regCPSR();
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SET_CPSR:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_set_regCPSR(cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_GET_SPSR:           // FIXME: NOT CORRECT
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_get_regCPSR();
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SET_SPSR:           // FIXME: NOT CORRECT
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_set_regCPSR(cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SET_MODE_THUMB:
  case JTAGARM7TDMI_SET_MODE_ARM:
	jtagarm7tdmi_resettap();
    cmddataword[0] = jtagarm7tdmi_setMode_ARM();
    txdata(app,verb,4);
    break;
    
  case 0xD0:          // loopback test
    jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_bypass(cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case 0xD8:          // EICE_READ
    jtagarm7tdmi_resettap();
    cmddatalong[0] = eice_read(cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case 0xD9:          // EICE_WRITE
    jtagarm7tdmi_resettap();
    cmddatalong[0] = eice_write(cmddatalong[0], cmddatalong[1]);
    txdata(app,verb,4);
    break;
  case 0xDA:          // TEST MSB THROUGH CHAIN0 and CHAIN1
    jtagarm7tdmi_resettap();
    jtagarm7tdmi_scan_intest(0);
    cmddatalong[0] = jtagarmtransn(0x41414141, 32, LSB, NOEND, NORETIDLE);
    cmddatalong[1] = jtagarmtransn(0x42424242, 32, MSB, NOEND, NORETIDLE);
    cmddatalong[2] = jtagarmtransn(0x43434343,  9, MSB, NOEND, NORETIDLE);
    cmddatalong[3] = jtagarmtransn(0x44444444, 32, MSB, NOEND, NORETIDLE);
    cmddatalong[4] = jtagarmtransn(cmddatalong[0], 32, LSB, NOEND, NORETIDLE);
    cmddatalong[5] = jtagarmtransn(cmddatalong[1], 32, MSB, NOEND, NORETIDLE);
    cmddatalong[6] = jtagarmtransn(cmddatalong[2],  9, MSB, NOEND, NORETIDLE);
    cmddatalong[7] = jtagarmtransn(cmddatalong[3], 32, MSB, END, RETIDLE);
    jtagarm7tdmi_resettap();
    jtagarm7tdmi_scan_intest(1);
    cmddatalong[8] = jtagarmtransn(0x41414141, 32, MSB, NOEND, NORETIDLE);
    cmddatalong[9] = jtagarmtransn(0x44444444,  1, MSB, NOEND, NORETIDLE);
    cmddatalong[10] = jtagarmtransn(cmddatalong[8], 32, MSB, NOEND, NORETIDLE);
    cmddatalong[11] = jtagarmtransn(cmddatalong[9],  1, MSB, END, RETIDLE);
    txdata(app,verb,48);
    break;
    
  default:
    jtaghandle(app,verb,len);
  }
}
