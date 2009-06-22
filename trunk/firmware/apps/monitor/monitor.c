#include "command.h"
#include "platform.h"

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
    //Todo, make word or byte.
    memorybyte[cmddataword[0]]=cmddata[2];
    cmddata[0]=memorybyte[cmddataword[0]];
    txdata(app,verb,1);
    break;
  case MONITOR_CHANGE_BAUD:
    //This command, and ONLY this command, does not reply.
    setbaud(cmddata[0]);
    //txdata(app,verb,0);
    break;
  }
}
