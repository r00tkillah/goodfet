/*! \file glitch.c
  \author Travis Goodspeed
  \brief PS2 Timing Monitor for GoodFET
  
  This module spies on PS/2.  For now, it just reports the
  inter-character timing information.
*/

#include "platform.h"
#include "command.h"
#include "ps2.h"
#include "jtag.h"


u32 mclock=0;
u32 clock=0;

// Timer A0 interrupt service routine
interrupt(TIMERA0_VECTOR) Timer_A (void)
{
  if(!clock++)
    mclock++;
  return;
}



/** Pins (Clk, Dat)
    TDI P5.1
    TDO P5.2
*/

// This is just a plugin for now.
#define ps2handle pluginhandle

u32 oldclock=0;
//! Handles a monitor command.
int ps2handle(unsigned char app,
	      unsigned char verb,
	      unsigned int len){
  
  switch(verb){
  case START:
    WDTCTL = WDTPW + WDTHOLD;             // Stop WDT
    TACTL = TASSEL1 + TACLR;              // SMCLK, clear TAR
    CCTL0 = CCIE;                         // CCR0 interrupt enabled
    CCR0 = 0x100; //clock divider
    TACTL |= MC_3;
    _EINT();                              // Enable interrupts 
    
    
    P5DIR&=~(TDI+TDO);//input mode
    P5OUT=0; // pull down
    
    debugstr("Waiting for a keypress.");
    //Wait for a keypress.
    
    while(1){
      //Debounce the 1s polling
      while((P5IN&TDI && P5IN&TDO))
	while((P5IN&TDI));// && P5IN&TDO));
      
      //Transmit the data only if it is new.
      if((clock-oldclock)>0x100){
	cmddatalong[0]=clock;//-oldclock;
	cmddatalong[0]-=oldclock;
	oldclock=clock;
	
	txdata(app,verb,4);
      }
    }
    break;
  case STOP:
  default:
    debugstr("Unknown ps2 verb.");
    txdata(app,NOK,0);
  }
}
