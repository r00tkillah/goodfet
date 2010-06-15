/*! \file gfports.h
  \author Travis Goodspeed
  \brief GoodFET Port Definitions
*/

#ifndef GFPORTS
#define GFPORTS

#include <io.h>

// N.B., only asm-clean CPP definitions allowed.

//Use false P5REN for 1612.
#ifdef __MSP430_HAS_PORT5__
#ifndef __MSP430_HAS_PORT5_R__
//#warning "1xx, using fake P5REN for external pulling resistors."
#define P5REN P5OUT
#endif
#endif

/*
//Use these instead of the explicit names.
#ifdef MSP430
#define gfout P5OUT
#define gfin  P5IN
#define gfdir P5DIR
#define gfren P5REN
#endif
*/


#endif //GFPORTS
