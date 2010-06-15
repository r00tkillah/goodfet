/*! \file ccspi.c
  \author Travis Goodspeed
  \brief Chipcon SPI Register Interface
*/

//Higher level left to client application.

#include "platform.h"
#include "command.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>

#include "ccspi.h"
#include "spi.h"


#define RADIOACTIVE SETCE
#define RADIOPASSIVE CLRCE

//! Set up the pins for CCSPI mode.
void ccspisetup(){
  SETSS;
  P5DIR&=~MISO;
  P5DIR|=MOSI+SCK;
  DIRSS;
  DIRCE;
  
  //Begin a new transaction.
  CLRSS; 
  SETSS;
}

//! Read and write an CCSPI byte.
u8 ccspitrans8(u8 byte){
  register unsigned int bit;
  //This function came from the CCSPI Wikipedia article.
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
u8 ccspi_regwrite(u8 reg, const u8 *buf, int len){
  CLRSS;
  
  reg=ccspitrans8(reg);
  while(len--)
    ccspitrans8(*buf++);
  
  SETSS;
  return reg;//status
}
//! Reads a register
u8 ccspi_regread(u8 reg, u8 *buf, int len){
  CLRSS;
  
  reg=ccspitrans8(reg);
  while(len--)
    *buf++=ccspitrans8(0);
  
  SETSS;
  return reg;//status
}

//! Handles a Chipcon SPI command.
void ccspihandle(unsigned char app,
	       unsigned char verb,
	       unsigned long len){
  unsigned long i;
  
  //Drop CE to passify radio.
  RADIOPASSIVE;
  //Raise !SS to end transaction, just in case we forgot.
  SETSS;
  ccspisetup();
  
  switch(verb){
    //PEEK and POKE might come later.
  case READ:  
  case WRITE:
    CLRSS; //Drop !SS to begin transaction.
    for(i=0;i<len;i++)
      cmddata[i]=ccspitrans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;

  case PEEK://Grab CCSPI Register
    CLRSS; //Drop !SS to begin transaction.
    ccspitrans8(CCSPI_R_REGISTER | cmddata[0]); //000A AAAA
    for(i=1;i<len;i++)
      cmddata[i]=ccspitrans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;
    
  case POKE://Poke CCSPI Register
    CLRSS; //Drop !SS to begin transaction.
    ccspitrans8(CCSPI_W_REGISTER | cmddata[0]); //001A AAAA
    for(i=1;i<len;i++)
      cmddata[i]=ccspitrans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;
  case SETUP:
    ccspisetup();
    txdata(app,verb,0);
    break;
  case CCSPI_RX:
    RADIOPASSIVE;
    //Get the packet.
    CLRSS;
    ccspitrans8(CCSPI_R_RX_PAYLOAD);
    for(i=0;i<32;i++)
      cmddata[i]=ccspitrans8(0xde);
    SETSS;
    //no break
    txdata(app,verb,32);
    break;
  case CCSPI_RX_FLUSH:
    //Flush the buffer.
    CLRSS;
    ccspitrans8(CCSPI_FLUSH_RX);
    SETSS;
    
    //Return the packet.
    txdata(app,verb,32);
    break;
  case CCSPI_TX:
  case CCSPI_TX_FLUSH:
  default:
    debugstr("Not yet supported.");
    txdata(app,verb,0);
    break;
  }
  

  SETSS;//End session
  RADIOACTIVE;
}
