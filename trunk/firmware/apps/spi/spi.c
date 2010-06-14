/*! \file spi.c
  \author Travis Goodspeed
  \brief SPI Master
*/

//Higher level left to client application.

#include "platform.h"
#include "command.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>

#include "spi.h"

//This could be more accurate.
//Does it ever need to be?
#define SPISPEED 0
#define SPIDELAY(x)
//delay(x)


//! Set up the pins for SPI mode.
void spisetup(){
  SETSS;
  P5DIR|=MOSI+SCK+BIT0; //BIT0 might be SS
  P5DIR&=~MISO;
  
  //Begin a new transaction.
  CLRSS; 
  SETSS;
}


//! Read and write an SPI byte.
unsigned char spitrans8(unsigned char byte){
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
 
    SETCLK;
  
    /* read MISO on trailing edge */
    byte |= READMISO;
    CLRCLK;
  }
  
  return byte;
}


//! Enable SPI writing
void spiflash_wrten(){
  SETSS;
  /*
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x04);//Write Disable
  SETSS;  //Raise !SS to end transaction.
  */
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x06);//Write Enable
  SETSS;  //Raise !SS to end transaction.
}


//! Grab the SPI flash status byte.
unsigned char spiflash_status(){
  unsigned char c;
  SETSS;  //Raise !SS to end transaction.
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x05);//GET STATUS
  c=spitrans8(0xFF);
  SETSS;  //Raise !SS to end transaction.
  return c;
}


//! Grab the SPI flash status byte.
void spiflash_setstatus(unsigned char c){
  SETSS;
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x01);//SET STATUS
  spitrans8(c);
  SETSS;  //Raise !SS to end transaction.
  //return c;
}


//! Read a block to a buffer.
void spiflash_peekblock(unsigned long adr,
			unsigned char *buf,
			unsigned int len){
  unsigned char i;
  
  SETSS;
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x03);//Flash Read Command
  
  //Send address
  spitrans8((adr&0xFF0000)>>16);
  spitrans8((adr&0xFF00)>>8);
  spitrans8(adr&0xFF);
  
  for(i=0;i<len;i++)
    buf[i]=spitrans8(0);
  SETSS;  //Raise !SS to end transaction.
}

//! Read a block to a buffer.
void spiflash_pokeblock(unsigned long adr,
			unsigned char *buf,
			unsigned int len){
  unsigned int i;
  
  SETSS;
  
  //if(len!=0x100)
  //  debugstr("Non-standard block size.");
  
  while(spiflash_status()&0x01);//minor performance impact
  
  spiflash_setstatus(0x02);
  spiflash_wrten();
  
  //Are these necessary?
  //spiflash_setstatus(0x02);
  //spiflash_wrten();
  
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x02); //Poke command.
  
  //Send address
  spitrans8((adr&0xFF0000)>>16);
  spitrans8((adr&0xFF00)>>8);
  spitrans8(adr&0xFF);

  for(i=0;i<len;i++)
    spitrans8(buf[i]);
  SETSS;  //Raise !SS to end transaction.
  
  while(spiflash_status()&0x01);//minor performance impact
  return;
}


//! Write many blocks to the SPI Flash.
void spiflash_pokeblocks(unsigned long adr,
			 unsigned char *buf,
			 unsigned int len){
  long off=0;//offset of this block
  int blen;//length of this block
  SETSS;
  
  while(off<len){
    //calculate block length
    blen=(len-off>0x100?0x100:len-off);
    //write the block
    spiflash_pokeblock(adr+off,
		       buf+off,
		       blen);
    //add offset
    off+=blen;
  }
}



//! Peek some blocks.
void spiflash_peek(unsigned char app,
		   unsigned char verb,
		   unsigned long len){
  unsigned int i;
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x03);//Flash Read Command
  len=3;//write 3 byte pointer
  for(i=0;i<len;i++)
    spitrans8(cmddata[i]);
  
  //Send reply header
  len=0x1000;
  txhead(app,verb,len);
  
  while(len--)
    serial_tx(spitrans8(0));
  
  SETSS;  //Raise !SS to end transaction.
}


//! Erase a sector.
void spiflash_erasesector(unsigned long adr){
  //debugstr("Erasing a 4kB sector.");

  //Write enable.
  spiflash_wrten();

  //Begin
  CLRSS;

  //Second command.
  spitrans8(0x20);
  //Send address
  spitrans8((adr&0xFF0000)>>16);
  spitrans8((adr&0xFF00)>>8);
  spitrans8(adr&0xFF);

  SETSS;
  while(spiflash_status()&0x01);//while busy
  //debugstr("Erased.");
}


//! Handles a monitor command.
void spihandle(unsigned char app,
	       unsigned char verb,
	       unsigned long len){
  unsigned long i;
  
  //Raise !SS to end transaction, just in case we forgot.
  SETSS;
  spisetup();
  
  switch(verb){
    //PEEK and POKE might come later.
  case READ:
  case WRITE:
    CLRSS; //Drop !SS to begin transaction.
    for(i=0;i<len;i++)
      cmddata[i]=spitrans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;


  case SPI_JEDEC://Grab 3-byte JEDEC ID.
    CLRSS; //Drop !SS to begin transaction.
    spitrans8(0x9f);
    len=3;  //Length is variable in some chips, 3 minimum.
    for(i=0;i<len;i++)
      cmddata[i]=spitrans8(cmddata[i]);
    txdata(app,verb,len);
    SETSS;  //Raise !SS to end transaction.
    break;


  case PEEK://Grab 128 bytes from an SPI Flash ROM
    spiflash_peek(app,verb,len);
    break;


  case POKE://Poke up bytes from an SPI Flash ROM.
    spiflash_pokeblocks(cmddatalong[0],//adr
			cmddata+4,//buf
			len-4);//len    
    
    txdata(app,verb,0);
    break;


  case SPI_ERASE://Erase the SPI Flash ROM.
    spiflash_wrten();
    CLRSS; //Drop !SS to begin transaction.
    spitrans8(0xC7);//Chip Erase
    SETSS;  //Raise !SS to end transaction.
    
    
    while(spiflash_status()&0x01)//while busy
      PLEDOUT^=PLEDPIN;
    PLEDOUT&=~PLEDPIN;
    
    txdata(app,verb,0);
    break;

  case SETUP:
    spisetup();
    txdata(app,verb,0);
    break;
  }
  
}
