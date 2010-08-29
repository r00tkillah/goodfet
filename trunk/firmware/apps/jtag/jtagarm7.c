/*! \file jtagarm7.c
  \brief ARM7TDMI JTAG (AT91R40008, AT91SAM7xxx)
*/

#include "platform.h"
#include "command.h"
#include "jtagarm7.h"


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

/*  WHAT SHOULD THIS MODULE DO?
 *     *start
 *     *shift_ir
 *     *shift_dr
 *      reset_tap
 *     *scanchain0
 *     *scanchain1 (instr_primitive)
 *     *scanchain2 (hmmmm... perhaps we'll need to keep the debug calls)
 *     *    eice_read
 *     *    eice_write
 *     *get_register
 *     *set_register
 */

// ! Start JTAG, setup pins, reset TAP and return IDCODE
void jtagarm7tdmi_start() {
  jtagsetup();
  SETTST;
  jtag_resettap();
}


u8 shift_ir(u8 ir, u8 flags){
  u8 retval;
  jtag_goto_shift_ir();
  retval = jtagtransn(ir, 4, LSB|flags); 
  return retval;
}

//!  Connect the appropriate scan chain to TDO/TDI.  SCAN_N, INTEST
unsigned long jtagarm7tdmi_scan(u8 chain, u8 testmode) {               // PROVEN
/*
When selecting a scan chain the “Run Test/Idle” state should never be reached, other-
wise, when in debug state, the core will not be correctly isolated and intrusive
commands occur. Therefore, it is recommended to pass directly from the “Update”
state” to the “Select DR” state each time the “Update” state is reached.
*/
  unsigned long retval;
  shift_ir(ARM7TDMI_IR_SCAN_N, NORETIDLE);
  jtag_goto_shift_dr();
  retval = jtagtransn(chain, 4, LSB | NORETIDLE);
  shift_ir(testmode, NORETIDLE); 
  return(retval);
}


/************************* EmbeddedICE Primitives ****************************/
//! shifter for writing to chain2 (EmbeddedICE). 
unsigned long eice_write(unsigned char reg, unsigned long data){
  unsigned long retval, temp;
  jtagarm7tdmi_scan(2, ARM7TDMI_IR_INTEST);
  jtag_goto_shift_dr();
  retval = jtagtransn(data, 32, LSB| NOEND| NORETIDLE);         // send in the data - 32-bits lsb
  temp = jtagtransn(reg, 5, LSB| NOEND| NORETIDLE);             // send in the register address - 5 bits lsb
  jtagtransn(1, 1, LSB);                                        // send in the WRITE bit
  return(retval); 
}

//! shifter for reading from chain2 (EmbeddedICE).
unsigned long eice_read(unsigned char reg){               // PROVEN
  unsigned long temp, retval;
  jtagarm7tdmi_scan(2, ARM7TDMI_IR_INTEST);
  jtag_goto_shift_dr();                                         // send in the register address - 5 bits LSB
  temp = jtagtransn(reg, 5, LSB| NOEND| NORETIDLE);
  jtagtransn(0L, 1, LSB);                                       // clear TDI to select "read only"
  jtag_goto_shift_dr();                                         // Now shift out the 32 bits
  retval = jtagtransn(0L, 32, LSB);                             // atmel arm jtag docs pp.10-11: LSB first
  return(retval);
  
}

//! push an instruction into the pipeline
unsigned long jtagarm7tdmi_instr_primitive(unsigned long instr, char breakpt){  // PROVEN
  unsigned long retval;
  jtagarm7tdmi_scan(1, ARM7TDMI_IR_INTEST);

  //debughex32(instr);
  jtag_goto_shift_dr();
  // if the next instruction is to run using MCLK (master clock), set TDI
  if (breakpt)
    {
    SETMOSI;
    } 
  else
    {
    CLRMOSI; 
    }
  jtag_tcktock();
  
  // Now shift in the 32 bits
  retval = jtagtransn(instr, 32, 0);    // Must return to RUN-TEST/IDLE state for instruction to enter pipeline, and causes debug clock.
  return(retval);
}

u32 jtagarm7tdmi_nop(u8 brkpt){
    //  WARNING: current_dbgstate must be up-to-date before calling this function!!!!!
    if (current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT)
        return jtagarm7tdmi_instr_primitive(THUMB_INSTR_NOP, brkpt);
    return jtagarm7tdmi_instr_primitive(ARM_INSTR_NOP, brkpt);
}

/******************** Complex Commands **************************/

//! Retrieve a 32-bit Register value
unsigned long jtagarm7_get_reg_prim(unsigned long instr){
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_instr_primitive(instr, 0);
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
  return jtagarm7tdmi_nop( 0);                          // recover 32-bit word
}

//! Set a 32-bit Register value
void jtagarm7_set_reg_prim(unsigned long instr, unsigned long reg, unsigned long val){      // PROVEN - 100827 (non-PC)
  jtagarm7tdmi_nop( 0);                                 // push nop into pipeline - executed 
  jtagarm7tdmi_instr_primitive(instr, 0);               // push instr into pipeline - fetch
    jtagarm7tdmi_nop( 0);                               // push nop into pipeline - decode 
    jtagarm7tdmi_nop( 0);                               // push nop into pipeline - execute 
    jtagarm7tdmi_instr_primitive(val, 0);               // push 32-bit word on data bus
  if (reg == ARM_REG_PC){
    debugstr("setting pc...");
    jtagarm7tdmi_nop( 0);                               // push nop into pipeline - refill 
    jtagarm7tdmi_nop( 0);                               // push nop into pipeline - refill 
  }
  jtagarm7tdmi_nop( 0);                               // push nop into pipeline - decode 
  jtagarm7tdmi_nop( 0);                               // push nop into pipeline - execute 
}

void jtagarm7_thumb_swap_reg(unsigned char dir, unsigned long reg){                         // PROVEN - 100827
  reg = reg & 7;
  jtagarm7tdmi_nop( 0);
  if (dir){
    jtagarm7tdmi_instr_primitive((unsigned long)(THUMB_INSTR_MOV_LoHi | (reg) | (reg<<16)), 0);
    debughex32((unsigned long)(THUMB_INSTR_MOV_LoHi | (reg) | (reg<<16)));
  } else {
    jtagarm7tdmi_instr_primitive((unsigned long)(THUMB_INSTR_MOV_HiLo | (reg<<3) | (reg<<19)), 0);
    debughex32((unsigned long)(THUMB_INSTR_MOV_HiLo | (reg<<3) | (reg<<19)));
  }
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
}
  
unsigned long jtagarm7tdmi_get_register(unsigned long reg) {                                // PROVEN - 100827
  unsigned long retval=0L, instr, r0;
  current_dbgstate = eice_read(EICE_DBGSTATUS);
  if (current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT){
    if (reg > 7){
      debugstr("debug: jtagarm7tdmi_get_register: thumb reg > 15");
      reg = reg & 7;
      r0 = jtagarm7_get_reg_prim( THUMB_READ_REG);          // save reg0
      jtagarm7_thumb_swap_reg(THUMB_SWAP_HiLo, reg);        // clobber reg0 with hi reg
      retval = jtagarm7_get_reg_prim( THUMB_READ_REG);      // recover 32-bit word
      jtagarm7_set_reg_prim( THUMB_WRITE_REG, 0, r0);       // restore r0
      return retval;
    } else {
      instr = (unsigned long)(THUMB_READ_REG | (unsigned long)reg | (unsigned long)(reg<<16L));
    }
  } else
    instr = (reg<<12L) | ARM_READ_REG;    // STR Rx, [R14] 
  return jtagarm7_get_reg_prim(instr);
}

//! Set a 32-bit Register value
//  writing to a register is a problem child in ARM, actually.  if the register you are using as the indirect offset register is misaligned, your results are misaligned.
//  this set_register implementation normalizes this process at the cost of performance.  since we don't know what's in the register, we set it to 0 first
//  we could use r14 and hope all is well, but only for arm, not thumb mode, and not always is all well then either.  this is a performance trade-off we may have to revisit later
//
void jtagarm7tdmi_set_register(unsigned long reg, unsigned long val) {                      // PROVEN - 100827
  unsigned long instr, r0;
  current_dbgstate = eice_read(EICE_DBGSTATUS);
  if (current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT){
    if (reg > 7){
      
      r0 = jtagarm7_get_reg_prim(THUMB_READ_REG);
      jtagarm7_set_reg_prim(THUMB_WRITE_REG, 0, 0);
      instr = (unsigned long)(THUMB_WRITE_REG | (unsigned long)reg | (unsigned long)(reg<<16L));
      jtagarm7_set_reg_prim(instr, reg, val);
      jtagarm7_thumb_swap_reg(THUMB_SWAP_LoHi, reg);                // place 32-bit word into a high register
      jtagarm7_set_reg_prim( THUMB_WRITE_REG, 0, r0);               // restore r0
    } else
      instr = THUMB_WRITE_REG | (reg) | ((reg)<<16) | ((reg)<<3) | ((reg)<<19);
  } else {
    instr = ARM_WRITE_REG | (reg<<12L) | (reg<<16); //  LDR Rx, [R14]
  }
  
  //debughex32(instr);
  //  --- first time to clear the register... this ensures the write is not 8-bit offset ---
  jtagarm7_set_reg_prim(instr, reg, 0);
  //  --- now we actually write to the register ---
  jtagarm7_set_reg_prim(instr, reg, val);
}


///////////////////////////////////////////////////////////////////////////////////////////////////
//! Handles ARM7TDMI JTAG commands.  Forwards others to JTAG.
void jtagarm7tdmihandle(unsigned char app, unsigned char verb, unsigned long len){
  unsigned int val;
 
  switch(verb){
  case START:
    //Enter JTAG mode.
    jtagarm7tdmi_start();
    txdata(app,verb,0);
    break;
  case JTAG_IR_SHIFT:
    cmddataword[0] = shift_ir(cmddata[0], cmddata[1]);
    txdata(app,verb,1);
    break;
  case JTAG_DR_SHIFT:
    jtag_goto_shift_dr();
    cmddatalong[0] = jtagtransn(cmddatalong[1],cmddata[0],cmddata[1]);
    txdata(app,verb,4);
    break;
  case JTAGARM7_CHAIN0:
    jtagarm7tdmi_scan(0, ARM7TDMI_IR_INTEST);
    jtag_goto_shift_dr();
    //debughex32(cmddatalong[0]);
    //debughex(cmddataword[4]);
    //debughex32(cmddatalong[1]);
    //debughex32(cmddatalong[3]);
    cmddatalong[0] = jtagtransn(cmddatalong[0], 32, LSB| NOEND| NORETIDLE);
    cmddatalong[2] = jtagtransn(cmddataword[4], 9, MSB| NOEND| NORETIDLE);
    cmddatalong[1] = jtagtransn(cmddatalong[1], 32, MSB| NOEND| NORETIDLE);
    cmddatalong[3] = jtagtransn(cmddatalong[3], 32, MSB);
    txdata(app,verb,16);
    break;
  case JTAGARM7_SCANCHAIN1:
  case JTAGARM7_DEBUG_INSTR:
    cmddatalong[0] = jtagarm7tdmi_instr_primitive(cmddatalong[0],cmddata[4]);
    txdata(app,verb,4);
    break;
  case JTAGARM7_EICE_READ:
    cmddatalong[0] = eice_read(cmddata[0]);
    txdata(app,verb,0x4);
    break;
  case JTAGARM7_EICE_WRITE:
    eice_write(cmddata[4], cmddatalong[0]);
    txdata(app,verb,0);
    break;
  case JTAGARM7_GET_REGISTER:
    val = cmddata[0];
    cmddatalong[0] = jtagarm7tdmi_get_register(val);
    txdata(app,verb,4);
    break;
  case JTAGARM7_SET_REGISTER:
    jtagarm7tdmi_set_register(cmddatalong[1], cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case JTAG_RESETTARGET:
    CLRTST;
    delay(10);
    SETTST;
    break;


  //case JTAGARM7_STEP_INSTR:
/*  case JTAGARM7_READ_CODE_MEMORY:
  case JTAGARM7_WRITE_FLASH_PAGE:
  case JTAGARM7_READ_FLASH_PAGE:
  case JTAGARM7_MASS_ERASE_FLASH:
  case JTAGARM7_PROGRAM_FLASH:
  case JTAGARM7_LOCKCHIP:
  case JTAGARM7_CHIP_ERASE:
  */
  default:
    jtaghandle(app,verb,len);
  }
}


