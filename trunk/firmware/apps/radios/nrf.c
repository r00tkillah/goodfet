/*! \file nrf.c
  \author Travis Goodspeed
  \brief NordicRF Register Interface
*/

//Higher level left to client application.

#include "platform.h"
#include "command.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>

#include "nrf.h"
#include "spi.h"

//This could be more accurate.
//Does it ever need to be?
#define NRFSPEED 0
#define NRFDELAY(x)
//delay(x)


//! Set up the pins for NRF mode.
void nrfsetup(){
  P5OUT|=SS;
  P5DIR|=MOSI+SCK+SS;
  P5DIR&=~MISO;
  
  //Begin a new transaction.
  P5OUT&=~SS; 
  P5OUT|=SS;
}


//! Read and write an NRF byte.
unsigned char nrftrans8(unsigned char byte){
  register unsigned int bit;
  //This function came from the NRF Wikipedia article.
  //Minor alterations.
  
  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      SETMOSI;
    else
      CLRMOSI;
    byte <<= 1;
 
    SETCLK;
  
    /* read MISO on trailing edge */
    byte |= READMISO;
    CLRCLK;
  }
  
  return byte;
}




//! Handles a Nordic RF command.
void nrfhandle(unsigned char app,
	       unsigned char verb,
	       unsigned long len){
  unsigned long i;
  
  //Raise !SS to end transaction, just in case we forgot.
  P5OUT|=SS;
  nrfsetup();
  
  switch(verb){
    //PEEK and POKE might come later.
  case READ:
  case WRITE:
    P5OUT&=~SS; //Drop !SS to begin transaction.
    for(i=0;i<len;i++)
      cmddata[i]=nrftrans8(cmddata[i]);
    P5OUT|=SS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;



  case PEEK://Grab NRF Register
    txdata(app,verb,0);
    break;
    
  case POKE://Poke NRF Register
    
    txdata(app,verb,0);
    break;
    
  case SETUP:
    nrfsetup();
    txdata(app,verb,0);
    break;
  }
  
}
