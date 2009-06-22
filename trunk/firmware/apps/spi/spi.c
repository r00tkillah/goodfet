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
  P5DIR|=MOSI+SCK+SS;
  P5DIR&=~MISO;
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

//! Handles a monitor command.
void spihandle(unsigned char app,
	       unsigned char verb,
	       unsigned char len){
  unsigned char i;
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
  case SETUP:
    spisetup();
    txdata(app,verb,0);
    break;
  }
}
