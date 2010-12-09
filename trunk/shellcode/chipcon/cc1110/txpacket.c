#include <cc1110.h>
#include "cc1110-ext.h"

char __xdata at 0xfe00 packet[256] ;

//! Transmit a packet out of the radio from 0xFE00.
void main(){
  unsigned char len=packet[0], i=0;
  RFST=RFST_STX;     //Begin transmit.
  while(i!=len+1){
    while(!RFTXRXIF); //Wait for byte to be ready.
    
    RFTXRXIF=0;      //Clear the flag.
    RFD=packet[i++]; //Send the next byte.
  }
  RFST = RFST_SIDLE; //End transmit.
  HALT;
}
