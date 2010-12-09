#include <cc1110.h>
#include "cc1110-ext.h"

char __xdata at 0xfe00 packet[256] ;


//! Receives a packet out of the radio from 0xFE00.
void main(){
  unsigned char len=100, i=0;
  RFST=RFST_SRX;     //Begin to receive.
  while(i!=len+1){
    while(RFTXRXIF); //Wait for byte to be ready.
    
    RFTXRXIF=0;      //Clear the flag.
    packet[i++]=RFD; //Grab the next byte.
    len=packet[0];   //First byte of the packet is the length.
  }
  RFST = RFST_SIDLE; //End transmit.
  HALT;
}
