/*! \file telosb.h
  \author Travis Goodspeed
  \brief Port descriptions for the TelosB platform.
  
  This file defines the Telos B hardware, so that the GoodFET firmware
  may be loaded onto it.  Adjustments include the !CS line of the CC2420
  radio, the choice of serial port, and the LEDs.

*/

#ifdef MSP430
#include <io.h>
#endif


//LED on P1.0
#define PLEDOUT P5OUT
#define PLEDDIR P5DIR
#define PLEDPIN BIT4


//Radio CS is P4.2
#define SETSS P4OUT|=BIT2
#define CLRSS P4OUT&=~BIT2
#define DIRSS P4DIR|=BIT2;


//CC2420 Chip Reset.  Need to document this.
#define SETCE P4OUT|=BIT6
#define CLRCE P4OUT&=~BIT6
#define DIRCE P4DIR|=BIT6
