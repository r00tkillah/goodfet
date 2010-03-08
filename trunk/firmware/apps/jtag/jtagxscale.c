/*! \file jtagxscale.c
  \author Dave Huseby <dave@linuxprogrammer.org>
  \brief Intel XScale JTAG (32-bit)
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"

//! Handles XScale JTAG commands.  Forwards others to JTAG.
void xscalehandle(unsigned char app,
                  unsigned char verb,
                  unsigned long len)
{    
    switch(verb) 
    {
        case START:
        case STOP:
        case PEEK:
        case POKE:
        default:
            jtaghandle(app,verb,len);
    }
}
