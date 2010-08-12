/*! \file jtag.c
  \author Travis Goodspeed <travis at radiantmachines.com>
  \brief Low-level JTAG
*/


#include "platform.h"
#include "command.h"
#include "jtag.h"


//! Set up the pins for JTAG mode.
void jtagsetup(){
  P5DIR|=MOSI+SCK+TMS;
  P5DIR&=~MISO;
  /*
  P5OUT|=0xFFFF;
  P5OUT=0;
  */
  P4DIR|=TST;
  P2DIR|=RST;
  msdelay(100);
}

/************************** JTAG Primitives ****************************/
// these have been turned into functions to save flash space
void jtag_tcktock() {
  CLRTCK; 
  PLEDOUT^=PLEDPIN; 
  SETTCK; 
  PLEDOUT^=PLEDPIN;
}

void jtag_goto_shift_ir() {
  SETTMS;
  jtag_tcktock();
  jtag_tcktock();
  CLRTMS;
  jtag_tcktock();
  jtag_tcktock();

}
void jtag_goto_shift_dr() {
  SETTMS;
  jtag_tcktock();
  CLRTMS;
  jtag_tcktock();
  jtag_tcktock();
}

void jtag_resettap(){
  SETTMS;
  jtag_tcktock();
  jtag_tcktock();
  jtag_tcktock();
  jtag_tcktock();
  jtag_tcktock();  // now in Reset state
  CLRTMS;
  jtag_tcktock();  // now in Run-Test/Idle state
}


int savedtclk=0;
//  NOTE: important: THIS MODULE REVOLVES AROUND RETURNING TO RUNTEST/IDLE, OR THE FUNCTIONAL EQUIVALENT
//! Shift N bits over TDI/TDO.  May choose LSB or MSB, and select whether to terminate (TMS-high on last bit) and whether to return to RUNTEST/IDLE
//      flags should be 0 for most uses.  
//      for the extreme case, flags should be  (NOEND|NORETDLE|LSB)
//      other edge cases can involve a combination of those three flags
//
//      the max bit-size that can be be shifted is 32-bits.  
//      for longer shifts, use the NOEND flag (which infers NORETIDLE so the additional flag is unnecessary)
//
//      NORETIDLE is used for special cases where (as with arm) the debug subsystem does not want to 
//      return to the RUN-TEST/IDLE state between setting IR and DR
unsigned long jtagtransn(unsigned long word, unsigned char bitcount, unsigned char flags){            
  unsigned char bit;
  unsigned long high = 1L;
  unsigned long mask;

  //for (bit=(bitcount-1)/8; bit>0; bit--)
  //  high <<= 8;
  //high <<= ((bitcount-1)%8);
  high <<= (bitcount-1);

  mask = high-1;

  SAVETCLK;
  if (flags & LSB) {
    for (bit = bitcount; bit > 0; bit--) {
      /* write MOSI on trailing edge of previous clock */
      if (word & 1)
        {SETMOSI;}
      else
        {CLRMOSI;}
      word >>= 1;

      if (bit==1 && !(flags & NOEND))
        SETTMS;//TMS high on last bit to exit.
       
      jtag_tcktock();

      /* read MISO on trailing edge */
      if (READMISO){
        word += (high);
      }
    }
  } else {
    for (bit = bitcount; bit > 0; bit--) {
      /* write MOSI on trailing edge of previous clock */
      if (word & high)
        {SETMOSI;}
      else
        {CLRMOSI;}
      word = (word & mask) << 1;

      if (bit==1 && !(flags & NOEND))
        SETTMS;//TMS high on last bit to exit.

      jtag_tcktock();

      /* read MISO on trailing edge */
      word |= (READMISO);
    }
  }
 

  RESTORETCLK;
  //SETMOSI;

  if (!(flags & NOEND)){
    // exit state
    jtag_tcktock();
    // update state
    if (!(flags & NORETIDLE)){
      CLRTMS;
      jtag_tcktock();
    }
  }
  return word;
}

//! Shift 8 bits in and out.
unsigned char jtagtrans8(unsigned char byte){
  unsigned int bit;
  SAVETCLK;
  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      {SETMOSI;}
    else
      {CLRMOSI;}
    byte <<= 1;
    
    if(bit==7)
      SETTMS;//TMS high on last bit to exit.
    
    TCKTOCK;
    /* read MISO on trailing edge */
    byte |= READMISO;
  }
  RESTORETCLK;
  
  // exit state
  TCKTOCK;
  // update state
  CLRTMS;
  TCKTOCK;
  
  return byte;
}

//! Shift n bits in and out.
/*unsigned long jtagtransn(unsigned long word,
			 unsigned int bitcount){
  unsigned int bit;
  //0x8000
  unsigned long high=0x8000;
  
  if(bitcount==20)
    high=0x80000;
  if(bitcount==16)
    high= 0x8000;
  
  SAVETCLK;
  
  for (bit = 0; bit < bitcount; bit++) {
    // write MOSI on trailing edge of previous clock *
    if (word & high)
      {SETMOSI;}
    else
      {CLRMOSI;}
    word <<= 1;
    
    if(bit==bitcount-1)
      SETTMS;//TMS high on last bit to exit.
    
    TCKTOCK;
    // read MISO on trailing edge *
    word |= READMISO;
  }
  
  if(bitcount==20){
    word = ((word << 16) | (word >> 4)) & 0x000FFFFF;
  }
  
  RESTORETCLK;
  
  // exit state
  TCKTOCK;
  // update state
  CLRTMS;
  TCKTOCK;
  
  return word;
}
*/

//! Stop JTAG, release pins
void jtag_stop(){
  P5OUT=0;
  P4OUT=0;
}

unsigned int drwidth=16;
//! Shift all bits of the DR.
unsigned long jtag_dr_shift20(unsigned long in){
  // idle
  SETTMS;
  TCKTOCK;
  // select DR
  CLRTMS;
  TCKTOCK;
  // capture IR
  TCKTOCK;
  
  // shift DR, then idle
  return(jtagtransn(in,20,0));
}


//! Shift 16 bits of the DR.
unsigned int jtag_dr_shift16(unsigned int in){
  // idle
  SETTMS;
  TCKTOCK;
  // select DR
  CLRTMS;
  TCKTOCK;
  // capture IR
  TCKTOCK;
  
  // shift DR, then idle
  return(jtagtransn(in,16,0));
}

//! Shift native width of the DR
unsigned long jtag_dr_shiftadr(unsigned long in){
  unsigned long out=0;
  
  // idle
  SETTMS;
  TCKTOCK;
  // select DR
  CLRTMS;
  TCKTOCK;
  // capture IR
  TCKTOCK;

  
  out=jtagtransn(in,drwidth,0);
  
  // shift DR, then idle
  return(out);
}


//! Shift 8 bits of the IR.
unsigned char jtag_ir_shift8(unsigned char in){
  // idle
  SETTMS;
  TCKTOCK;
  // select DR
  TCKTOCK;
  // select IR
  CLRTMS;
  TCKTOCK;
  // capture IR
  TCKTOCK;
  
  // shift IR, then idle.
  return(jtagtrans8(in));
}

//! Handles a monitor command.
void jtaghandle(unsigned char app,
	       unsigned char verb,
	       unsigned long len){
  switch(verb){
    //START handled by specific JTAG
  case STOP:
    jtag_stop();
    txdata(app,verb,0);
    break;
  case SETUP:
    jtagsetup();
    txdata(app,verb,0);
    break;
  case JTAG_IR_SHIFT:
    cmddata[0]=jtag_ir_shift8(cmddata[0]);
    txdata(app,verb,1);
    break;
  case JTAG_DR_SHIFT:
    cmddataword[0]=jtag_dr_shift16(cmddataword[0]);
    txdata(app,verb,2);
    break;
  case JTAG_RESETTAP:
    jtag_resettap();
    txdata(app,verb,0);
    break;
  default:
    txdata(app,NOK,0);
  }
}


