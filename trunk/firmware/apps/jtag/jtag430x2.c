/*! \file jtag430x2.c
  \author Travis Goodspeed <travis at radiantmachines.com>
  
  This is an implementation of the MSP430X2 JTAG protocol
  for the GoodFET project at http://goodfet.sf.net/
  
  See the license file for details of proper use.
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"

unsigned char jtagid;

//! Get the JTAG ID
unsigned char jtag430x2_jtagid(){
  jtag430_resettap();
  return jtagid=jtag_ir_shift8(IR_BYPASS);
}
//! Start JTAG, take pins
unsigned char jtag430x2_start(){
  jtagsetup();
  P1OUT^=1;
  
  //Known-good starting position.
  //Might be unnecessary.
  SETTST;
  SETRST;
  
  delay(0xFFFF);
  
  //Entry sequence from Page 67 of SLAU265A for 4-wire MSP430 JTAG
  CLRRST;
  delay(10);
  CLRTST;
  delay(5);
  SETTST;
  msdelay(5);
  SETRST;
  P5DIR&=~RST;
  
  delay(0xFFFF);
  
  //Perform a reset and disable watchdog.
  return jtag430x2_jtagid();
}


//! Handles classic MSP430 JTAG commands.  Forwards others to JTAG.
void jtag430x2handle(unsigned char app,
		   unsigned char verb,
		   unsigned char len){
  
  switch(verb){
  case START:
    //Enter JTAG mode.
    do cmddata[0]=jtag430x2_start();
    while(cmddata[0]==00 || cmddata[0]==0xFF);
    
    //TAP setup, fuse check
    //jtag430_resettap();
    txdata(app,verb,1);
    break;
  case JTAG430_HALTCPU:
  case JTAG430_RELEASECPU:
  case JTAG430_SETINSTRFETCH:
  case JTAG430_READMEM:
  case PEEK:
  case JTAG430_WRITEMEM:
  case POKE:
  case JTAG430_WRITEFLASH:
  case JTAG430_ERASEFLASH:
  case JTAG430_SETPC:
  default:
    jtaghandle(app,verb,len);
  }
  jtag430_resettap();
}
