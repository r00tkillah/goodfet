/*! \file glitch.h
  \author Travis Goodspeed
  \brief Glitch handler functions.
*/

#include <signal.h>
#include <io.h>
#include <iomacros.h>

//! Disable glitch state at init.
void glitchsetup();
//! Setup analog chain for glitching.
void glitchsetupdac();
