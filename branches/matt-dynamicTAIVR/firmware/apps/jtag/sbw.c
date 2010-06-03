/*! \file sbw.c
  \author Travis Goodspeed and Mark Rages
  \brief Spy-Bi-Wire Mod of JTAG430 and JTAG430X
  
  As SBW is merely a multiplexed method of handling JTAG signals, this
  module works by replacing preprocessor definitions in the
  traditional modules to make them SBW compatible.  Function pointers
  would be size efficient, but so it goes.
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"
#include "sbw.h"

void sbwsetup(){
  /* To select the 2-wire SBW mode, the SBWTDIO line is held high and
     the first clock is applied on SBWTCK. After this clock, the
     normal SBW timings are applied starting with the TMS slot, and
     the normal JTAG patterns can be applied, typically starting with
     the Tap Reset and Fuse Check sequence.  The SBW mode is exited by
     holding the TEST/SWBCLK low for more than 100 μs. 
  */

  // tdio up, tck low
  //   
  P5OUT &= ~SBWTCK;
  P5OUT |= SBWTDIO;
  P5DIR |= SBWTDIO|SBWTCK;

  msdelay(1);
  SBWCLK();

  SBWCLK();

  // now we're in SBW mode
}

void sbwhandle(u8 app, u8 verb, u8 len){
  debugstr("Coming soon.");
  txdata(app,NOK,0);
}



//FIXME these should be prefixed with sbw
//to prevent name pollution.
int tms=1, tdi=1, tdo=0;

void clock_sbw() {
  //exchange TMS
  SETSBWIO(tms);
  SBWCLK();
  
  //exchange TDI
  SETSBWIO(tdi);
  SBWCLK();
  
  //exchange TDO
  P5DIR &= ~SBWTDIO; //input mode
  P5OUT &= ~SBWTCK;  //Drop Metaclock
  tdo=!!(P5IN & SBWTDIO);
  P5OUT |= SBWTCK;   //output mode
  P5DIR |= SBWTDIO;  //Raise Metaclock
  
  //TCK implied
}


void sbwSETTCLK(){
  SETSBWIO(tms);
  SBWCLK();

  SETSBWIO(1);asm("nop");asm("nop");	 
  SETSBWIO(0);asm("nop");asm("nop");	 
  SETSBWIO(1);asm("nop");asm("nop");	 
  SETSBWIO(0);asm("nop");asm("nop");	 
  SETSBWIO(1);asm("nop");asm("nop");	 

  SBWCLK();
  
  P5DIR &= ~SBWTDIO;
  P5OUT &= ~SBWTCK; 
  //tdo=!!(P5IN & SBWTDIO);
  P5OUT |= SBWTCK;
  P5DIR |= SBWTDIO; 
}

void sbwCLRTCLK(){
  SETSBWIO(tms);
  SBWCLK();

  SETSBWIO(0);asm("nop");asm("nop");	 
  SETSBWIO(1);asm("nop");asm("nop");	 
  SETSBWIO(0);asm("nop");asm("nop");	 
  SETSBWIO(1);asm("nop");asm("nop");	 
  SETSBWIO(0);asm("nop");asm("nop");	 

  SBWCLK();

  P5DIR &= ~SBWTDIO;
  P5OUT &= ~SBWTCK; 
  //tdo=!!(P5IN & SBWTDIO);
  P5OUT |= SBWTCK;
  P5DIR |= SBWTDIO;   
}

