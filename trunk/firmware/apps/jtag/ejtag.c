/*! \file ejtag.c
  \author Travis Goodspeed <travis at radiantmachines.com>
  \brief MIPS EJTAG (32-bit)
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"

//! Handles MIPS EJTAG commands.  Forwards others to JTAG.
void ejtaghandle(unsigned char app,
		   unsigned char verb,
		   unsigned long len){
    
  switch(verb){
  case START:
    cmddata[0]=jtag_ir_shift8(IR_BYPASS);
    txdata(app,verb,1);
    break;
  case STOP:
    txdata(app,verb,0);
    break;
  case PEEK:
    //WRITEME
  case POKE:
    //WRITEME
  default:
    jtaghandle(app,verb,len);
  }
}
