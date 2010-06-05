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

//Weird HOPE badge wiring.  This was a fuckup.
//BIT0 should be SS, but in point of fact it is IRQ.
//BIT4 is actually SS, BIT5 is CE.
#define SS BIT4
#define CE BIT5;

#define RADIOACTIVE  P5OUT|=CE
#define RADIOPASSIVE P5OUT&=~CE


//! Set up the pins for NRF mode.
void nrfsetup(){
  P5OUT|=SS;
  P5DIR&=~MISO;
  P5DIR|=MOSI+SCK+SS+CE;
  
  
  //Begin a new transaction.
  P5OUT&=~SS; 
  P5OUT|=SS;
}

//! Read and write an NRF byte.
u8 nrftrans8(u8 byte){
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


//! Writes a register
u8 nrf_regwrite(u8 reg, const u8 *buf, int len){
  P5OUT&=~SS;
  
  reg=nrftrans8(reg);
  while(len--)
    nrftrans8(*buf++);
  
  P5OUT|=SS;
  return reg;//status
}
//! Reads a register
u8 nrf_regread(u8 reg, u8 *buf, int len){
  P5OUT&=~SS;
  
  reg=nrftrans8(reg);
  while(len--)
    *buf++=nrftrans8(0);
  
  P5OUT|=SS;
  return reg;//status
}

//! Handles a Nordic RF command.
void nrfhandle(unsigned char app,
	       unsigned char verb,
	       unsigned long len){
  unsigned long i;
  
  //Drop CE to passify radio.
  RADIOPASSIVE;
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
    P5OUT&=~SS; //Drop !SS to begin transaction.
    nrftrans8(NRF_R_REGISTER | cmddata[0]); //000A AAAA
    for(i=1;i<len;i++)
      cmddata[i]=nrftrans8(cmddata[i]);
    P5OUT|=SS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;
    
  case POKE://Poke NRF Register
    P5OUT&=~SS; //Drop !SS to begin transaction.
    nrftrans8(NRF_W_REGISTER | cmddata[0]); //001A AAAA
    for(i=1;i<len;i++)
      cmddata[i]=nrftrans8(cmddata[i]);
    P5OUT|=SS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;
  case SETUP:
    nrfsetup();
    txdata(app,verb,0);
    break;
  case NRF_RX:
    RADIOPASSIVE;
    //Get the packet.
    P5OUT&=~SS;
    nrftrans8(NRF_R_RX_PAYLOAD);
    for(i=0;i<32;i++)
      cmddata[i]=nrftrans8(0xde);
    P5OUT|=SS;
    //no break
    txdata(app,verb,32);
    break;
  case NRF_RX_FLUSH:
    //Flush the buffer.
    P5OUT&=~SS;
    nrftrans8(NRF_FLUSH_RX);
    P5OUT|=SS;
    
    //Return the packet.
    txdata(app,verb,32);
    break;
  case NRF_TX:
  case NRF_TX_FLUSH:
  default:
    debugstr("Not yet supported.");
    txdata(app,verb,0);
    break;
  }
  

  P5OUT|=SS;//End session
  RADIOACTIVE;
}
