/*! \file nhbadge.h
  \author Travis Goodspeed
  \brief Port descriptions for the Next Hope Badge.
*/


#ifdef MSP430
#include <io.h>
#endif


//LED on P1.0
#define PLEDOUT P1OUT
#define PLEDDIR P1DIR
#define PLEDPIN BIT0


//No longer works for Hope badge.
#define SETSS P5OUT|=BIT4
#define CLRSS P5OUT&=~BIT4
#define DIRSS P5DIR|=BIT4;

//BIT5 is Chip Enable
//#define RADIOACTIVE  P5OUT|=BIT5
//#define RADIOPASSIVE P5OUT&=~BIT5
#define SETCE P5OUT|=BIT5
#define CLRCE P5OUT&=~BIT5
#define DIRCE P5DIR|=BIT5
