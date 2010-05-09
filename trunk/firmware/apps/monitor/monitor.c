/*! \file monitor.c
  \author Travis Goodspeed
  \brief Local debug monitor.
*/

#include "command.h"
#include "platform.h"
#include "monitor.h"

//! Call a function by address.
int fncall(unsigned int adr){
  int (*machfn)() = 0;
  machfn= (int (*)()) adr;
  return machfn();
}

//! Handles a monitor command.
void monitorhandle(unsigned char app,
		   unsigned char verb,
		   unsigned long len){
  switch(verb){
  default:
    debugstr("ERROR: Command unsupported by debug monitor.");
    break;
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
  case CALL:
    //Set the program counter to cmdword[0];
    cmddataword[0]=fncall(cmddataword[0]);
    txdata(app,verb,2);
    break;
  case EXEC:
    //Execute the argument as code from RAM.
    cmddataword[0]=fncall((u16) cmddataword);
    txdata(app,verb,2);
    break;
  case MONITOR_SIZEBUF:
    //TODO make the data length target-specific, varying by ram.
    cmddataword[0]=0x100;
    txdata(app,verb,2);
    break;
  case MONITOR_CHANGE_BAUD:
    //This command, and ONLY this command, does not reply.
    setbaud(cmddata[0]);
    //txdata(app,verb,0);
    break;
  case MONITOR_RAM_PATTERN:
    monitor_ram_pattern();//reboots, will never return
    break;
  case MONITOR_RAM_DEPTH:
    cmddataword[0]=monitor_ram_depth();
    txdata(app,verb,2);
    break;
  case MONITOR_DIR:
    P5DIR=cmddata[0];
    txdata(app,verb,1);
    break;
  case MONITOR_IN:
    cmddata[0]=P5IN;
    txdata(app,verb,1);
    break;
  case MONITOR_OUT:
    P5OUT=cmddata[0];
    txdata(app,verb,1);
    break;
  case MONITOR_SILENT:
    silent=cmddata[0];
    txdata(app,verb,1);
    break;
  case MONITOR_CONNECTED:
    msp430_init_dco_done();
    txdata(app,verb,0);
    break;
  }
}

//! Overwrite all of RAM with 0xBEEF, then reboot.
void monitor_ram_pattern(){
  register int *a;
  
  //Wipe all of ram.
  for(a=(int*)0x1100;a<(int*)0x2500;a++){//TODO get these from the linker.
    *((int*)a) = 0xBEEF;
  }
  txdata(0x00,0x90,0);
  
  //Reboot
  #ifdef MSP430
  asm("br &0xfffe");
  #endif
}

//! Return the number of contiguous bytes 0xBEEF, to measure RAM usage.
unsigned int monitor_ram_depth(){
  register int a;
  register int count=0;
  for(a=0x1100;a<0x2500;a+=2)
    if(*((int*)a)==0xBEEF) count+=2;
  
  return count;
}
