/*! \file glitch.h
  \author Travis Goodspeed
  \brief Glitch handler functions.
*/

#include <signal.h>
#include <io.h>
#include <iomacros.h>

//Command codes
#define GLITCHAPP      0x80
#define GLITCHVERB     0x81
#define GLITCHVOLTAGES 0x90
#define GLITCHRATE     0x91

//! Setup glitching.
void glitchsetup();
//! Setup analog chain for glitching.
void glitchsetupdac();
//! Call this before the function to be glitched.
void glitchprime();

extern u16 glitchH, glitchL, glitchstate, glitchcount;

//! Glitch an application.
void glitchapp(u8 app);
//! Set glitching voltages.
void glitchvoltages(u16 low, u16 high);
//! Set glitching rate.
void glitchrate(u16 rate);

//! Handles a monitor command.
void glitchhandle(unsigned char app,
		  unsigned char verb,
		  unsigned long len);
