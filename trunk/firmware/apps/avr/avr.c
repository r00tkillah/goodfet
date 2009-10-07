/*! \file avr.c
  \author Travis Goodspeed
  \brief AVR SPI Programmer
*/

#include "platform.h"
#include "command.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>

#include "avr.h"

//! Setup the AVR pins.
void avrsetup(){
  spisetup();
}

//! Initialized an attached AVR.
void avrconnect(){
  register int i;
  avrsetup();//set I/O pins
  
  //Pulse !RST (SS) at least twice while CLK is low.
  CLRSS;
  CLRCLK;
  
  for(i=0;i<5;i++){
    SETSS;
    CLRSS;
  }
  
  //Enable programming
  avr_prgen();
}

//! Perform a 4-byte exchange.
u8 avrexchange(u8 a, u8 b, u8 c, u8 d){
  spitrans8(a);
  spitrans8(b);
  if(spitrans8(c)!=b){
    debugstr("AVR sync error, b not returned as c.");
  }
  spitrans8(c);
  return spitrans8(d);
}

//! Enable AVR programming mode.
void avr_prgen(){
  avrexchange(0xac, 0x53, 0, 0);
}

//! Read AVR device code.
u8 avr_devicecode(){
  return avrexchange(0x30, //Read signature byte
	      0x00,
	      0x00, //&0x03 is sig adr
	      0x00 //don't care.
	      );
}

//! Handles an AVR command.
void avrhandle(unsigned char app,
	       unsigned char verb,
	       unsigned long len){
  unsigned long i;
  
  
  switch(verb){
  case READ:
  case WRITE:
    for(i=0;i<len;i++)
      cmddata[i]=spitrans8(cmddata[i]);
    txdata(app,verb,len);
    break;
  case SETUP:
    avrsetup();
    txdata(app,verb,0);
    break;
  case START:
    avrconnect();
    txdata(app,verb,0);
    break;
  case PEEK:
  case POKE:
  default:
    debugstr("Verb unimplemented in AVR application.");
    txdata(app,NOK,0);
    break;
  }
}

