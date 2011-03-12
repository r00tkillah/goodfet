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
#ifdef FIFOP
     //Has there been an overflow?
    if((!FIFO)&&FIFOP){
      debugstr("Clearing overflow");
      CLRSS;
      ccspitrans8(0x08); //SFLUSHRX
      SETSS;
    }
    
    //Is there a packet?
    if(FIFOP&&FIFO){
      //Wait for completion.
      while(SFD);
      
      //Get the packet.
      CLRSS;
      ccspitrans8(CCSPI_RXFIFO | 0x40);
      //ccspitrans8(0x3F|0x40);
      cmddata[0]=0xff; //to be replaced with length
      for(i=0;i<cmddata[0]+2;i++)
	cmddata[i]=ccspitrans8(0xde);
      SETSS;
      
      //Flush buffer.
      CLRSS;
      ccspitrans8(0x08); //SFLUSHRX
      SETSS;
      //Only should transmit length of one more than the reported
      // length of the frame, which holds the length byte:
      txdata(app,verb,cmddata[0]+1);
    }else{
      //No packet.
      txdata(app,verb,0);
    }
#else
    debugstr("Can't RX a packet with SFD and FIFOP definitions.");
    txdata(app,NOK,0);
#endif
    break;
  case CCSPI_RX_FLUSH:
    //Flush the buffer.
    CLRSS;
    ccspitrans8(CCSPI_SFLUSHRX);
    SETSS;
    
    txdata(app,verb,0);
    break;
  case CCSPI_REFLEX:
    debugstr("Coming soon.");
    txdata(app,verb,0);
    break;
  case CCSPI_TX_FLUSH:
     //Flush the buffer.
    CLRSS;
    ccspitrans8(CCSPI_SFLUSHTX);
    SETSS;
    
    txdata(app,verb,0);
    break;
  case CCSPI_TX:
#ifdef FIFOP
    
    //Wait for last packet to TX.
    //while(ccspi_status()&BIT3);
    
    //Load the packet.
    CLRSS;
    ccspitrans8(CCSPI_TXFIFO);
    for(i=0;i<cmddata[0];i++)
      ccspitrans8(cmddata[i]);
    SETSS;
    
    //Transmit the packet.
    CLRSS;
    ccspitrans8(0x04); //STXON
    SETSS;
    
    //Wait for the pulse on SFD, after which the packet has been sent.
    while(!SFD);
    while(SFD);
    
    //Flush TX buffer.
    CLRSS;
    ccspitrans8(0x09); //SFLUSHTX
    SETSS;
    
    txdata(app,verb,0);
#else
    debugstr("Can't TX a packet with SFD and FIFOP definitions.");
    txdata(app,NOK,0);
#endif
    break;
  default:
    debugstr("Not yet supported in CCSPI");
    txdata(app,verb,0);
    break;
  }
  

}
