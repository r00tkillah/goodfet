/*! \file jtag430.c
  \author Travis Goodspeed <travis at radiantmachines.com>
  \brief MSP430 JTAG (16-bit)
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"


unsigned int jtag430mode=MSP430X2MODE;

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
  jtag430_haltcpu();
  
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

//! Write data to flash memory.  Must be preconfigured.
void jtag430_writeflashword(unsigned int adr, unsigned int data){
  
  CLRTCLK;
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x2408);//word write
  jtag_ir_shift8(IR_ADDR_16BIT);
  jtag_dr_shift16(adr);
  jtag_ir_shift8(IR_DATA_TO_ADDR);
  jtag_dr_shift16(data);
  SETTCLK;
  
  //Return to read mode.
  CLRTCLK;
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x2409);
  
  /*
  jtag430_writemem(adr,data);
  CLRTCLK;
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x2409);
  */
  
  //Pulse TCLK
  jtag430_tclk_flashpulses(35); //35 standard
}

//! Configure flash, then write a word.
void jtag430_writeflash(unsigned int adr, unsigned int data){
  jtag430_haltcpu();
  
  //FCTL1=0xA540, enabling flash write
  jtag430_writemem(0x0128, 0xA540);
  //FCTL2=0xA540, selecting MCLK as source, DIV=1
  jtag430_writemem(0x012A, 0xA540);
  //FCTL3=0xA500, should be 0xA540 for Info Seg A on 2xx chips.
  jtag430_writemem(0x012C, 0xA500); //all but info flash.
  
  //Write the word itself.
  jtag430_writeflashword(adr,data);
  
  //FCTL1=0xA500, disabling flash write
  jtag430_writemem(0x0128, 0xA500);
  
  //jtag430_releasecpu();
}



//! Power-On Reset
void jtag430_por(){
  unsigned int jtagid;

  // Perform Reset
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x2C01); // apply
  jtag_dr_shift16(0x2401); // remove
  CLRTCLK;
  SETTCLK;
  CLRTCLK;
  SETTCLK;
  CLRTCLK;
  jtagid = jtag_ir_shift8(IR_ADDR_CAPTURE); // get JTAG identifier
  SETTCLK;
  
  jtag430_writemem(0x0120, 0x5A80);   // Diabled Watchdog
}



#define ERASE_GLOB 0xA50E
#define ERASE_ALLMAIN 0xA50C
#define ERASE_MASS 0xA506
#define ERASE_MAIN 0xA504
#define ERASE_SGMT 0xA502

//! Configure flash, then write a word.
void jtag430_eraseflash(unsigned int mode, unsigned int adr, unsigned int count){
  jtag430_haltcpu();
  
  //FCTL1= erase mode
  jtag430_writemem(0x0128, mode);
  //FCTL2=0xA540, selecting MCLK as source, DIV=1
  jtag430_writemem(0x012A, 0xA540);
  //FCTL3=0xA500, should be 0xA540 for Info Seg A on 2xx chips.
  jtag430_writemem(0x012C, 0xA500);
  
  //Write the erase word.
  jtag430_writemem(adr, 0x55AA);
  //Return to read mode.
  CLRTCLK;
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x2409);
  
  //Send the pulses.
  jtag430_tclk_flashpulses(count);
  
  //FCTL1=0xA500, disabling flash write
  jtag430_writemem(0x0128, 0xA500);
  
  //jtag430_releasecpu();
}


//! Reset the TAP state machine.
void jtag430_resettap(){
  int i;
  // Settle output
  SETTDI; //430X2
  SETTMS;
  //SETTDI; //classic
  TCKTOCK;

  // Navigate to reset state.
  // Should be at least six.
  for(i=0;i<4;i++){
    TCKTOCK;
  }

  // test-logic-reset
  CLRTMS;
  TCKTOCK;
  SETTMS;
  // idle

    
  /* sacred, by spec.
     Sometimes this isn't necessary.  */
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

  #ifndef SBWREWRITE
  //Entry sequence from Page 67 of SLAU265A for 4-wire MSP430 JTAG
  CLRRST;
  delay(100); //100
  CLRTST;
  delay(50);  //50
  SETTST;
  delay(50);  //50
  SETRST;
  P5DIR&=~RST;
  delay(0xFFFF);
  #endif
  
  //Perform a reset and disable watchdog.
  jtag430_por();
  jtag430_writemem(0x120,0x5a80);//disable watchdog
  
  jtag430_haltcpu();
}

//! Start normally, not JTAG.
void jtag430_stop(){
  debugstr("Exiting JTAG.");
  jtagsetup();
  
  //Known-good starting position.
  //Might be unnecessary.
  //SETTST;
  CLRTST;
  SETRST;
  delay(0xFFFF);
  
  //Entry sequence from Page 67 of SLAU265A for 4-wire MSP430 JTAG
  CLRRST;
  delay(0xFFFF);
  SETRST;
  //P5DIR&=~RST;
  //delay(0xFFFF);
  
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


//! Handles classic MSP430 JTAG commands.  Forwards others to JTAG.
void jtag430handle(unsigned char app,
		   unsigned char verb,
		   unsigned long len){
  unsigned long at;
  unsigned int i, val;
  
  //debugstr("Classic MSP430 handler.");
  
  
  /* FIXME
   * Sometimes JTAG doesn't init correctly.
   * This restarts the connection if the masked-rom
   * chip ID cannot be read.  Should print warning
   * for testing server.
   */
  while((i=jtag430_readmem(0xff0))==0xFFFF){
    jtag430_start();
    P1OUT^=1;
  }
  P1OUT&=~1;
    
  switch(verb){
  case START:
    //Enter JTAG mode.
    jtag430_start();
    //TAP setup, fuse check
    jtag430_resettap();
    
    cmddata[0]=jtag_ir_shift8(IR_BYPASS);    
    txdata(app,verb,1);

    break;
  case STOP:
    jtag430_stop();
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
    at=cmddatalong[0];
    
    //Fetch large blocks for bulk fetches,
    //small blocks for individual peeks.
    if(len>5)
      len=(cmddataword[2]);//always even.
    else
      len=2;
    len&=~1;//clear lsbit
    
    txhead(app,verb,len);
    for(i=0;i<len;i+=2){
      jtag430_resettap();
      val=jtag430_readmem(at);
      
      at+=2;
      serial_tx(val&0xFF);
      serial_tx((val&0xFF00)>>8);
    }
    break;
  case JTAG430_WRITEMEM:
  case POKE:
    jtag430_haltcpu();
    jtag430_writemem(cmddataword[0],cmddataword[2]);
    cmddataword[0]=jtag430_readmem(cmddataword[0]);
    txdata(app,verb,2);
    break;
    /*
  case JTAG430_WRITEFLASH:

    //debugstr("Poking flash memory.");
    jtag430_writeflash(cmddataword[0],cmddataword[2]);
    
    //Try again if failure.
    //if(cmddataword[2]!=jtag430_readmem(cmddataword[0]))
    //  jtag430_writeflash(cmddataword[0],cmddataword[2]);
    
    //Return result.
    cmddataword[0]=jtag430_readmem(cmddataword[0]);
    
    txdata(app,verb,2);
    break; */
  case JTAG430_WRITEFLASH:
    at=cmddataword[0];
    
    for(i=0;i<(len>>1)-2;i++){
      //debugstr("Poking flash memory.");
      jtag430_writeflash(at+(i<<1),cmddataword[i+2]);
      //Reflash if needed.  Try this twice to save grace?
      if(cmddataword[i]!=jtag430_readmem(at))
	jtag430_writeflash(at+(i<<1),cmddataword[i+2]);
    }
    
    //Return result of first write as a word.
    cmddataword[0]=jtag430_readmem(cmddataword[0]);
    
    txdata(app,verb,2);
    break;
  case JTAG430_ERASEFLASH:
    jtag430_eraseflash(ERASE_MASS,0xFFFE,0x3000);
    txdata(app,verb,0);
    break;
  case JTAG430_SETPC:
    jtag430_haltcpu();
    jtag430_setpc(cmddataword[0]);
    txdata(app,verb,0);
    break;
    
  case JTAG430_COREIP_ID:
  case JTAG430_DEVICE_ID:
    cmddataword[0]=0;
    cmddataword[1]=0;
    txdata(app,verb,4);
    break;
    
  default:
    jtaghandle(app,verb,len);
  }
  //jtag430_resettap();  //DO NOT UNCOMMENT
}
