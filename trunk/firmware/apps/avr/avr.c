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
  //set I/O pins
  avrsetup();
  
  //Pulse !RST (SS) at least twice while CLK is low.
  CLRCLK;
  CLRSS;

  SETSS;
  CLRCLK;
  delay(500);
  CLRSS;
  delay(500);
  
  //Enable programming
  avr_prgen();
}

//! Read and write an SPI byte with delays.
unsigned char avrtrans8(unsigned char byte){
  register unsigned int bit;
  //This function came from the SPI Wikipedia article.
  //Minor alterations.
  
  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      SETMOSI;
    else
      CLRMOSI;
    byte <<= 1;
    
    delay(2);
    SETCLK;
  
    /* read MISO on trailing edge */
    byte |= READMISO;
    delay(2);
    CLRCLK;
  }
  
  return byte;
}

//! Perform a 4-byte exchange.
u8 avrexchange(u8 a, u8 b, u8 c, u8 d){
  avrtrans8(a);
  avrtrans8(b);
  if(avrtrans8(c)!=b){
    debugstr("AVR sync error, b not returned as c.");
    //Reconnect here?
  }
  return avrtrans8(d);
}

//! Enable AVR programming mode.
void avr_prgen(){
  avrexchange(0xAC, 0x53, 0, 0);
}

//! Read AVR device code.
u8 avr_sig(u8 i){
  return avrexchange(0x30, //Read signature byte
	      0x00,
	      i&0x03,      //sig adr
	      0x00         //don't care.
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
  case START://returns device code
    avrconnect();
    //no break here
  case AVR_PEEKSIG:
    for(i=0;i<4;i++)
      cmddata[i]=avr_sig(i);
    txdata(app,verb,4);
    break;
  case PEEK:
  case POKE:
  default:
    debugstr("Verb unimplemented in AVR application.");
    txdata(app,NOK,0);
    break;
  }
}

