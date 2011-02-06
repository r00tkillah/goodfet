/*! \file ccspi.c
  \author Travis Goodspeed
  \brief Chipcon SPI Register Interface
  
  Unfortunately, there is very little similarity between the CC2420
  and the CC2500, to name just two of the myriad of Chipcon SPI
  radios.  Auto-detection will be a bit difficult, but more to the
  point, all high level functionality must be moved into the client.
*/

//Higher level left to client application.

#include "platform.h"
#include "command.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>

#include "ccspi.h"
#include "spi.h"

//! Handles a Chipcon SPI command.
void ccspi_handle_fn( uint8_t const app,
					  uint8_t const verb,
					  uint32_t const len);

// define the ccspi app's app_t
app_t const ccspi_app = {

	/* app number */
	CCSPI,

	/* handle fn */
	ccspi_handle_fn,

	/* name */
	"CCSPI",

	/* desc */
	"\tThe CCSPI app adds support for the Chipcon SPI register\n"
	"\tinterface. Unfortunately, there is very little similarity\n"
	"\tbetween the CC2420 and the CC2500, to name just two of the\n"
	"\tmyriad of Chipcon SPI radios.  Auto-detection will be a bit\n"
	"\tdifficult, but more to the point, all high level functionality\n"
	"\tmust be moved into the client.\n"
};

//! Set up the pins for CCSPI mode.
void ccspisetup(){
  SPIDIR&=~MISO;
  SPIDIR|=MOSI+SCK;
  DIRSS;
  DIRCE;
  
  P4OUT|=BIT5; //activate CC2420 voltage regulator
  msdelay(100);
  
  //Reset the CC2420.
  P4OUT&=~BIT6;
  P4OUT|=BIT6;
  
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
void ccspi_handle_fn( uint8_t const app,
		      uint8_t const verb,
		      uint32_t const len){
  unsigned long i;
  
  //debugstr("Chipcon SPI handler.");
  
  switch(verb){
  case PEEK:
    cmddata[0]|=0x40; //Set the read bit.
    //DO NOT BREAK HERE.
  case READ:
  case WRITE:
  case POKE:
    CLRSS; //Drop !SS to begin transaction.
    for(i=0;i<len;i++)
      cmddata[i]=ccspitrans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;
  case SETUP:
    ccspisetup();
    txdata(app,verb,0);
    break;
  case CCSPI_RX:
    //Get the packet.
    CLRSS;
    ccspitrans8(CCSPI_RXFIFO);
    for(i=0;i<32;i++)
      cmddata[i]=ccspitrans8(0xde);
    SETSS;
    //no break
    txdata(app,verb,32);
    break;
  case CCSPI_RX_FLUSH:
    //Flush the buffer.
    CLRSS;
    ccspitrans8(CCSPI_SFLUSHRX);
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
  

}
