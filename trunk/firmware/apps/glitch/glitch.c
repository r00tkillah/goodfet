/*! \file glitch.c
  \author Travis Goodspeed
  \brief Glitching Support for GoodFET20
  
  See the TI example MSP430x261x_dac12_01.c for usage of the DAC.
  This module sends odd and insufficient voltages on P6.6/DAC0
  in order to bypass security restrictions of target devices.
*/

#include "platform.h"
#include "command.h"
#include "glitch.h"

//! Disable glitch state at init.
void glitchsetup(){
#ifdef DAC12IR
  //Set GSEL high to disable glitching.

  P5DIR|=0x80;
  P6DIR|=0x40;  
  
  P5OUT|=0x80;
  P6OUT|=0x40;
  
  glitchsetupdac();
#endif
}

//! Setup analog chain for glitching.
void glitchsetupdac(){
  glitchvoltages(glitchL,glitchH);
}


u16 glitchH=0xfff, glitchL=0xfff,
  glitchstate, glitchcount;

//! Glitch an application.
void glitchapp(u8 app){
  debugstr("That app is not yet supported.");
}
//! Set glitching voltages.
void glitchvoltages(u16 low, u16 high){
  int i;
  glitchH=high;
  glitchL=low;
  
  
  #ifdef DAC12IR
  ADC12CTL0 = REF2_5V + REFON;                  // Internal 2.5V ref on
  // Delay here for reference to settle.
  for(i=0;i!=0xFFFF;i++) asm("nop");
  DAC12_0CTL = DAC12IR + DAC12AMP_5 + DAC12ENC; // Int ref gain 1
  // 1.0V 0x0666, 2.5V 0x0FFF
  DAC12_0DAT = high;
  //DAC12_0DAT = 0x0880;
  #endif 
}
//! Set glitching rate.
void glitchrate(u16 rate){
  glitchcount=rate;
}


//! Handles a monitor command.
void glitchhandle(unsigned char app,
		  unsigned char verb,
		  unsigned long len){
  switch(verb){
  case GLITCHVOLTAGES:
    glitchvoltages(cmddataword[0],
		   cmddataword[1]);
    txdata(app,verb,0);
    break;
  case GLITCHRATE:
    glitchrate(cmddataword[0]);
    txdata(app,verb,0);
    break;
  case START:
  case STOP:
  case GLITCHAPP:
  case GLITCHVERB:
  default:
    debugstr("Unknown glitching verb.");
    txdata(app,NOK,0);
  }
}
