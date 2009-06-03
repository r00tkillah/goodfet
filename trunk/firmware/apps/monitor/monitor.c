#include "command.h"

//! Handles a monitor command.
void monitorhandle(unsigned char app,
		   unsigned char verb,
		   unsigned char len){
  switch(verb){
  case PEEK:
    cmddata[0]=memorybyte[cmddataword[0]];
    txdata(app,verb,1);
    break;
  case POKE:
    break;
  }
}
