#include <cc1110.h>
#include "cc1110-ext.h"

//! Start the crystal oscillator at 26MHz.
void main(){
  SLEEP &= ~SLEEP_OSC_PD; // Turn both high speed oscillators on
  while( !(SLEEP & SLEEP_XOSC_S) ); // Wait until xtal oscillator is stable
  CLKCON = (CLKCON & ~(CLKCON_CLKSPD | CLKCON_OSC)) | CLKSPD_DIV_1; // Select xtal osc, 26 MHz
  while (CLKCON & CLKCON_OSC); // Wait for change to take effect
  SLEEP |= SLEEP_OSC_PD; // Turn off the other high speed oscillator (the RC osc)
  
  HALT;
}
