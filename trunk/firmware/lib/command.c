/*! \file command.c
  \author Travis Goodspeed
  \brief These functions manage command interpretation.
*/

#include "command.h"
#include "platform.h"
#include <string.h>

unsigned char cmddata[CMDDATALEN];
unsigned char silent=0;

//! Transmit a string.
void txstring(unsigned char app,
	      unsigned char verb,
	      const char *str){
  unsigned long len=strlen(str);
  txhead(app,verb,len);
  while(len--)
    serial_tx(*(str++));
}

/*! \brief Transmit a debug string.
  
  Transmits a debugging string that is to be printed
  out of line by the client.  This is just for record-keeping;
  it is not considered a proper reply to a query.
 */
void debugstr(const char *str){
  txstring(0xFF,0xFF,str);
}


//! Transmit a header.
void txhead(unsigned char app,
	    unsigned char verb,
	    unsigned long len){
  serial_tx(app);
  serial_tx(verb);
  //serial_tx(len);
  txword(len);
}

//! Transmit data.
void txdata(unsigned char app,
	    unsigned char verb,
	    unsigned long len){
  unsigned int i=0;
  if(silent)
    return;
  txhead(app,verb,len);
  for(i=0;i<len;i++){
    serial_tx(cmddata[i]);
  }
}

//! Receive a long.
unsigned long rxlong(){
  unsigned long toret=0;
  toret=serial_rx();
  toret|=(((long)serial_rx())<<8);
  toret|=(((long)serial_rx())<<16);
  toret|=(((long)serial_rx())<<24);
  return toret;
}
//! Receive a word.
unsigned int rxword(){
  unsigned long toret=0;
  toret=serial_rx();
  toret|=(((long)serial_rx())<<8);
  return toret;
}
//! Transmit a long.
void txlong(unsigned long l){
  serial_tx(l&0xFF);
  l>>=8;
  serial_tx(l&0xFF);
  l>>=8;
  serial_tx(l&0xFF);
  l>>=8;
  serial_tx(l&0xFF);
  l>>=8;
}
//! Transmit a word.
void txword(unsigned int l){
  serial_tx(l&0xFF);
  l>>=8;
  serial_tx(l&0xFF);
  l>>=8;
}

//Be very careful changing delay().
//It was chosen poorly by trial and error.

//! Delay for a count.
void delay(unsigned int count){
  volatile unsigned int i=count;
  while(i--) asm("nop");
}
//! MSDelay
void msdelay(unsigned int ms){
  volatile unsigned int i,j;
  i=100;
  while(i--){
    j=ms;
    while(j--) asm("nop");
  }
  //Using TimerA might be cleaner.
}
