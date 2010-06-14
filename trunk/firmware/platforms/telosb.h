/*! \file telosb.h
  \author Travis Goodspeed
  \brief Port descriptions for the TelosB platform.
  
  This file defines the Telos B hardware, so that the GoodFET firmware
  may be loaded onto it.  Adjustments include the !CS line of the CC2420
  radio, the choice of serial port, and the LEDs.

*/


//LED on P1.0
#define PLEDOUT P5OUT
#define PLEDDIR P5DIR
#define PLEDPIN BIT4

