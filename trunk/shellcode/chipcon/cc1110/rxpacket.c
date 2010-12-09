#include <cc1110.h>
#include "cc1110-ext.h"

#define MAXLEN 0xFF
char __xdata at 0xfe00 packet[MAXLEN] ;

//! Receives a packet out of the radio from 0xFE00.
void main(){
  unsigned char len=16, i=0;
  
  //1-out the buffer.
  for(i=0;i<64;i++)
    packet[i]=0xFF;
  i=0;
  
  //Disable interrupts.
  RFTXRXIE=0;
  
  //idle a bit.
  RFST=RFST_SIDLE;
  while(MARCSTATE!=MARC_STATE_IDLE);
  
  //Begin to receive.
  RFST=RFST_SRX;
  while(MARCSTATE!=MARC_STATE_RX);
  
  while(i<len+1){
    while(!RFTXRXIF); //Wait for byte to be ready.
    RFTXRXIF=0;      //Clear the flag.
    
    if (MARCSTATE == MARC_STATE_RX) {
      packet[i]=RFD; //Grab the next byte.
      i++;
      len=packet[0];   //First byte of the packet is the length.
    }else
      HALT;

  }
  RFST = RFST_SIDLE; //End transmit.
  HALT;
}
