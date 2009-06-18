
#include "platform.h"
#include "command.h"
#include "jtag.h"


//! Set the program counter.
void jtag430_setpc(unsigned int adr){
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x3401);// release low byte
  jtag_ir_shift8(IR_DATA_16BIT);
  jtag_dr_shift16(0x4030);//Instruction to load PC
  CLRTCLK;
  SETTCLK;
  jtag_dr_shift16(adr);// Value for PC
  CLRTCLK;
  jtag_ir_shift8(IR_ADDR_CAPTURE);
  SETTCLK;
  CLRTCLK ;// Now PC is set to "PC_Value"
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x2401);// low byte controlled by JTAG
}

//! Halt the CPU
void jtag430_haltcpu(){
  //jtag430_setinstrfetch();
  
  jtag_ir_shift8(IR_DATA_16BIT);
  jtag_dr_shift16(0x3FFF);//JMP $+0
  
  CLRTCLK;
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x2409);//set JTAG_HALT bit
  SETTCLK;
}

//! Release the CPU
void jtag430_releasecpu(){
  CLRTCLK;
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x2401);
  jtag_ir_shift8(IR_ADDR_CAPTURE);
  SETTCLK;
}

//! Read data from address
unsigned int jtag430_readmem(unsigned int adr){
  unsigned int toret;
  
  CLRTCLK;
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  if(adr>0xFF)
    jtag_dr_shift16(0x2409);//word read
  else
    jtag_dr_shift16(0x2419);//byte read
  jtag_ir_shift8(IR_ADDR_16BIT);
  jtag_dr_shift16(adr);//address
  jtag_ir_shift8(IR_DATA_TO_ADDR);
  SETTCLK;

  CLRTCLK;
  toret=jtag_dr_shift16(0x0000);//16 bit return
  
  return toret;
}

//! Write data to address.
void jtag430_writemem(unsigned int adr, unsigned int data){
  CLRTCLK;
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  if(adr>0xFF)
    jtag_dr_shift16(0x2408);//word write
  else
    jtag_dr_shift16(0x2418);//byte write
  jtag_ir_shift8(IR_ADDR_16BIT);
  jtag_dr_shift16(adr);
  jtag_ir_shift8(IR_DATA_TO_ADDR);
  jtag_dr_shift16(data);
  SETTCLK;
  
}

//! Write data to address.
void jtag430_writeflash(unsigned int adr, unsigned int data){
  //TODO; this is complicated.
}


//! Reset the TAP state machine.
void jtag430_resettap(){
  int i;
  // Settle output
  SETTMS;
  SETTDI;
  SETTCK;

  // Navigate to reset state.
  // Should be at least six.
  for(i=0;i<4;i++){
    CLRTCK;
    SETTCK;
  }

  // test-logic-reset
  CLRTCK;
  CLRTMS;
  SETTCK;
  SETTMS;
  // idle

    
  /* sacred, by spec.
     Sometimes this isn't necessary. */
  // fuse check
  CLRTMS;
  delay(50);
  SETTMS;
  CLRTMS;
  delay(50);
  SETTMS;
  /**/
  
}

//! Start JTAG, take pins
void jtag430_start(){
  jtagsetup();
  
  //Known-good starting position.
  //Might be unnecessary.
  SETTST;
  SETRST;
  delay(0xFFFF);
  
  //Entry sequence from Page 67 of SLAU265A for 4-wire MSP430 JTAG
  CLRRST;
  delay(100);
  CLRTST;
  delay(50);
  SETTST;
  delay(50);
  SETRST;
  P5DIR&=~RST;
  delay(0xFFFF);
}

//! Set CPU to Instruction Fetch
void jtag430_setinstrfetch(){
  jtag_ir_shift8(IR_CNTRL_SIG_CAPTURE);

  // Wait until instruction fetch state.
  while(1){
    if (jtag_dr_shift16(0x0000) & 0x0080)
      return;
    CLRTCLK;
    SETTCLK;
  }
}

//! Handles unique MSP430 JTAG commands.  Forwards others to JTAG.
void jtag430handle(unsigned char app,
		   unsigned char verb,
		   unsigned char len){
  unsigned char i;
  switch(verb){
  case START:
    //Enter JTAG mode.
    jtag430_start();
    //TAP setup, fuse check
    jtag430_resettap();
    txdata(app,verb,0);
    break;
  case JTAG430_HALTCPU:
    jtag430_haltcpu();
    txdata(app,verb,0);
    break;
  case JTAG430_RELEASECPU:
    jtag430_releasecpu();
    txdata(app,verb,0);
    break;
  case JTAG430_SETINSTRFETCH:
    jtag430_setinstrfetch();
    txdata(app,verb,0);
    break;

    
  case JTAG430_READMEM:
  case PEEK:
    cmddataword[0]=jtag430_readmem(cmddataword[0]);
    txdata(app,verb,2);
    break;
  case JTAG430_WRITEMEM:
  case POKE:
    jtag430_writemem(cmddataword[0],cmddataword[1]);
    txdata(app,verb,0);
    break;
  case JTAG430_WRITEFLASH:
    jtag430_writeflash(cmddataword[0],cmddataword[1]);
    txdata(app,verb,0);
    break;
  case JTAG430_SETPC:
    jtag430_setpc(cmddataword[0]);
    txdata(app,verb,0);
    break;
  default:
    jtaghandle(app,verb,len);
  }
}

