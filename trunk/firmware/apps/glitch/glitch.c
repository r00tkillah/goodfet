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
#ifdef DAC12IR
  int i;
  ADC12CTL0 = REF2_5V + REFON;                  // Internal 2.5V ref on
  // Delay here for reference to settle.
  for(i=0;i!=0xFFFF;i++) asm("nop");
  DAC12_0CTL = DAC12IR + DAC12AMP_5 + DAC12ENC; // Int ref gain 1
  // 1.0V 0x0666, 2.5V 0x0FFF
  DAC12_0DAT = 0x0FFF;
  //DAC12_0DAT = 0x0880;
  //__bis_SR_register(LPM0_bits + GIE);           // Enter LPM0
#endif 
}
