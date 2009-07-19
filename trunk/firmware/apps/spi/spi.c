//GoodFET SPI Application
//Handles basic I/O

//Higher level left to client application.

#include "platform.h"
#include "command.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>


//Pins and I/O
#define SS   BIT0
#define MOSI BIT1
#define MISO BIT2
#define SCK  BIT3

//This could be more accurate.
//Does it ever need to be?
#define SPISPEED 0
#define SPIDELAY(x) delay(x)

#define SETMOSI P5OUT|=MOSI
#define CLRMOSI P5OUT&=~MOSI
#define SETCLK P5OUT|=SCK
#define CLRCLK P5OUT&=~SCK
#define READMISO (P5IN&MISO?1:0)



//! Set up the pins for SPI mode.
void spisetup(){
  P5OUT|=SS;
  P5DIR|=MOSI+SCK+SS;
  P5DIR&=~MISO;
  
  //Begin a new transaction.
  P5OUT&=~SS; 
  P5OUT|=SS;
}

//! Read and write an SPI bit.
unsigned char spitrans8(unsigned char byte){
  unsigned int bit;
  //This function came from the SPI Wikipedia article.
  //Minor alterations.
  
  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      SETMOSI;
    else
      CLRMOSI;
    byte <<= 1;
 
    /* half a clock cycle before leading/rising edge */
    SPIDELAY(SPISPEED/2);
    SETCLK;
 
    /* half a clock cycle before trailing/falling edge */
    SPIDELAY(SPISPEED/2);
 
    /* read MISO on trailing edge */
    byte |= READMISO;
    CLRCLK;
  }
  
  return byte;
}

//! Enable SPI writing
void spiflash_wrten(){
  P5OUT&=~SS; //Drop !SS to begin transaction.
  spitrans8(0x04);//Write Disable
  P5OUT|=SS;  //Raise !SS to end transaction.
  P5OUT&=~SS; //Drop !SS to begin transaction.
  spitrans8(0x06);//Write Enable
  P5OUT|=SS;  //Raise !SS to end transaction.
}

//! Grab the SPI flash status byte.
unsigned char spiflash_status(){
  unsigned char c;
  P5OUT|=SS;  //Raise !SS to end transaction.
  P5OUT&=~SS; //Drop !SS to begin transaction.
  spitrans8(0x05);//GET STATUS
  c=spitrans8(0xFF);
  P5OUT|=SS;  //Raise !SS to end transaction.
  return c;
}
//! Grab the SPI flash status byte.
void spiflash_setstatus(unsigned char c){
  P5OUT&=~SS; //Drop !SS to begin transaction.
  spitrans8(0x01);//SET STATUS
  spitrans8(c);
  P5OUT|=SS;  //Raise !SS to end transaction.
  return c;
}

//! Handles a monitor command.
void spihandle(unsigned char app,
	       unsigned char verb,
	       unsigned char len){
  unsigned char i;
  
  
  //Raise !SS to end transaction, just in case we forgot.
  P5OUT|=SS;  
  
  switch(verb){
    //PEEK and POKE might come later.
  case READ:
  case WRITE:
    P5OUT&=~SS; //Drop !SS to begin transaction.
    for(i=0;i<len;i++)
      cmddata[i]=spitrans8(cmddata[i]);
    P5OUT|=SS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;
  case SPI_JEDEC://Grab 3-byte JEDEC ID.
    P5OUT&=~SS; //Drop !SS to begin transaction.
    spitrans8(0x9f);
    len=3;
    for(i=0;i<len;i++)
      cmddata[i]=spitrans8(cmddata[i]);
    txdata(app,verb,len);
    P5OUT|=SS;  //Raise !SS to end transaction.
    break;
  case PEEK://Grab 128 bytes from an SPI Flash ROM
    P5OUT&=~SS; //Drop !SS to begin transaction.
    spitrans8(0x03);//Flash Read Command
    len=3;//write 3 byte pointer
    for(i=0;i<len;i++)
      spitrans8(cmddata[i]);
    len=0x80;//128 byte chunk
    for(i=0;i<len;i++)
      cmddata[i]=spitrans8(0);
    P5OUT|=SS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;
  case POKE://Poke up bytes from an SPI Flash ROM.
    spiflash_setstatus(0x02);
    spiflash_wrten();
    
    P5OUT&=~SS; //Drop !SS to begin transaction.
    spitrans8(0x02); //Poke command.
    
    //First three bytes are address, then data.
    for(i=0;i<len;i++)
      spitrans8(cmddata[i]);
    P5OUT|=SS;  //Raise !SS to end transaction.
    while(spiflash_status()&0x01);//while busy
    txdata(app,verb,len);
    break;
  case SPI_ERASE://Erase the SPI Flash ROM.
    spiflash_wrten();
    P5OUT&=~SS; //Drop !SS to begin transaction.
    spitrans8(0xC7);//Chip Erase
    P5OUT|=SS;  //Raise !SS to end transaction.
    txdata(app,verb,0);
    break;
  case SETUP:
    spisetup();
    txdata(app,verb,0);
    break;
  }
  
}
