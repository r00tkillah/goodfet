/*! \file goodfet.h
  \author Travis Goodspeed
  \brief Port descriptions for the GoodFET platform.
  
*/




//LED on P1.0
#define PLEDOUT P1OUT
#define PLEDDIR P1DIR
#define PLEDPIN BIT0


//Use P3 instead of P5 for target I/O on chips without P5.
#ifndef __MSP430_HAS_PORT5__
#ifndef __MSP430_HAS_PORT5_R__
//#warning "No P5, using P3 instead.  Will break 2618 and 1612 support."
#define P5OUT P3OUT
#define P5DIR P3DIR
#define P5REN P3REN
#define P5IN P3IN
#endif
#endif

//No longer works for Hope badge.
#define SETSS P5OUT|=BIT0
#define CLRSS P5OUT&=~BIT0


