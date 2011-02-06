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


/* For the radio to be used:
   4.6 (!RST) must be low
   4.5 (VREF_EN) must be high
   4.2 (!CS) must be low for the transaction.
*/

#define INITPLATFORM \
  P1DIR = 0xe0;\
  P1OUT = 0x00;\
  P2DIR = 0x7b;\
  P2OUT = 0x10;\
  P3DIR = 0xf1;\
  P3OUT = 0x00;\
  P4DIR = 0xfd;\
  P4OUT = 0xFd;\
  P5DIR = 0xff;\
  P5OUT = 0xff;\
  P6DIR = 0xff;\
  P6OUT = 0x00;

//Radio CS is P4.2
#define SETSS P4OUT|=BIT2
#define CLRSS P4OUT&=~BIT2
#define DIRSS P4DIR|=BIT2


//Flash CS is P4.4, redefine only for the SPI app.
#ifdef SPIAPPLICATION
#undef SETSS
#undef CLRSS
#undef DIRSS
#define SETSS P4OUT|=BIT4
#define CLRSS P4OUT&=~BIT4
#define DIRSS P4DIR|=BIT4
#endif

//CC2420 Chip Enable
#define SETCE P4OUT|=BIT6
#define CLRCE P4OUT&=~BIT6
#define DIRCE P4DIR|=BIT6
