/*! \file gfports.h
  \author Travis Goodspeed
  \brief GoodFET Port Definitions
*/

#ifndef GFPORTS
#define GFPORTS

#include <io.h>

// N.B., only asm-clean CPP definitions allowed.

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

//Use false P5REN for 1612.
#ifdef __MSP430_HAS_PORT5__
#ifndef __MSP430_HAS_PORT5_R__
//#warning "1xx, using fake P5REN for external pulling resistors."
#define P5REN P5OUT
#endif
#endif


#endif //GFPORTS
