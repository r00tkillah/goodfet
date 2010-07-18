/*! \file nhbadge.h
  \author Travis Goodspeed
  \brief Port descriptions for the Next Hope Badge.
*/


#ifdef MSP430
#include <io.h>
#endif

#define P5OUT P4OUT
#define P5DIR P4DIR
#define P5IN P4IN
#define P5REN P4REN


//LED on P1.0
#define PLEDOUT P1OUT
#define PLEDDIR P1DIR
#define PLEDPIN BIT0


//No longer works for Hope badge.
#define SETSS P4OUT|=BIT4
#define CLRSS P4OUT&=~BIT4
#define DIRSS P4DIR|=BIT4;

//BIT5 is Chip Enable
//#define RADIOACTIVE  P4OUT|=BIT5
//#define RADIOPASSIVE P4OUT&=~BIT5
#define SETCE P4OUT|=BIT5
#define CLRCE P4OUT&=~BIT5
#define DIRCE P4DIR|=BIT5
