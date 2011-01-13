/*! \file sbw.h
  \author Travis Goodspeed and Mark Rages
  \brief Spy-Bi-Wire Stuff
*/

#ifndef SBW_H
#define SBW_H

#include "platform.h"
#include "command.h"
#include "app.h"

//IO Pins; these are for EZ430, not GoodFET/UIF
#define SBWTCK  BIT3
#define SBWTDIO BIT2

//This should be universal, move to jtag.h
#define TCKTOCK CLRTCK,SETTCK

//If SBW is defined, rewrite JTAG functions to be SBW.
#ifdef SBWREWRITE
#define jtagsetup sbwsetup

// I/O Redefintions
extern int tms, tdi, tdo;
#define SETTMS tms=1
#define CLRTMS tms=0
#define SETTDI tdi=1
#define CLRTDI tdi=0
#define TCKTOCK clock_sbw()
#define SETMOSI SETTDI
#define CLRMOSI CLRTDI
#define READMISO tdo

#endif

//! Enter SBW mode.
void sbwsetup();

//! Handle a SBW request.
void sbwhandle(u8 app, u8 verb, u8 len);

//! Perform a SBW bit transaction.
void clock_sbw();
//! Set the TCLK line, performing a transaction.
void sbwSETTCLK();
//! Clear the line.
void sbwCLRTCLK();

// Macros
#define SBWCLK() do { \
    P5OUT &= ~SBWTCK; \
    asm("nop");	      \
    asm("nop");	      \
    asm("nop");	      \
    P5OUT |= SBWTCK;  \
  } while (0)
#define SETSBWIO(x) do { 			\
  if (x)					\
    P5OUT |= SBWTDIO;				\
  else						\
    P5OUT &= ~SBWTDIO;				\
  } while (0)
#undef RESTORETCLK
#define RESTORETCLK do {			\
    if(savedtclk) {				\
      SETTCLK; 					\
    } else {					\
      CLRTCLK;					\
    }						\
  } while (0);
#undef SETTCLK
#define SETTCLK do {				\
    sbwSETTCLK();				\
    savedtclk=1;				\
  } while (0);
#undef CLRTCLK
#define CLRTCLK do {				\
    sbwCLRTCLK();				\
    savedtclk=0;				\
  } while (0); 

#undef SAVETCLK
//Do nothing for this.
#define SAVETCLK 

#endif // SBW_H

