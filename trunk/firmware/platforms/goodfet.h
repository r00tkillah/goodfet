/*! \file goodfet.h
  \author Travis Goodspeed
  \brief Port descriptions for the GoodFET platform.
*/

#include <signal.h>
#include <io.h>
#include <iomacros.h>


//LED on P1.0
#define PLEDOUT P1OUT
#define PLEDDIR P1DIR
#define PLEDPIN BIT0

//Use P3 instead of P5 for target I/O on chips without P5.
#ifdef msp430x2274
//#warning "No P5, using P3 instead.  Will break 2618 and 1612 support."
#define P5OUT P3OUT
#define P5DIR P3DIR
#define P5IN P3IN
#define P5REN P3REN
#endif

//This is how things used to work, don't do it anymore.
//#ifdef msp430x1612
//#define P5REN somedamnedextern
//#endif

//No longer works for Hope badge.
#define SETSS P5OUT|=BIT0
#define CLRSS P5OUT&=~BIT0
#define DIRSS P5DIR|=BIT0;

//BIT5 is Chip Enable.  Need to document this
//#define RADIOACTIVE  P5OUT|=BIT5
//#define RADIOPASSIVE P5OUT&=~BIT5
#define SETCE P5OUT|=BIT5
#define CLRCE P5OUT&=~BIT5
#define DIRCE P5DIR|=BIT5