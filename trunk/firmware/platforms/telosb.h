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

//LED on P5.4
#define PLEDOUT P5OUT
#define PLEDDIR P5DIR
#define PLEDPIN BIT4


#define SPIOUT P3OUT
#define SPIDIR P3DIR
#define SPIIN  P3IN
#define SPIREN P3REN
 
#define P5OUT P3OUT
#define P5DIR P3DIR
#define P5IN  P3IN
#define P5REN P3REN


/* For the radio to be used:
   4.6 (!RST) must be low
   4.5 (VREF_EN) must be high
   4.2 (!CS) must be low for the transaction.
*/

#define INITPLATFORM \
  P4DIR|=BIT6+BIT5+BIT2+BIT7+BIT4; \
  P4OUT=BIT5;

//Radio CS is P4.2
#define SETSS P4OUT|=BIT2
#define CLRSS P4OUT&=~BIT2
#define DIRSS P4DIR|=BIT2

//Flash CS is P4.4
//#define SETSS P4OUT|=BIT4
//#define CLRSS P4OUT&=~BIT4
//#define DIRSS P4DIR|=BIT4


//CC2420 Chip Reset.  Need to document this.
#define SETCE P4OUT|=BIT6
#define CLRCE P4OUT&=~BIT6
#define DIRCE P4DIR|=BIT6
