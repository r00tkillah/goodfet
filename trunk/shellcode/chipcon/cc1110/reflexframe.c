#include <cc1110.h>
#include "cc1110-ext.h"

char __xdata at 0xfe00 packet[256] ;

void sleepMillis(int ms) {
	int j;
	while (--ms > 0) { 
		for (j=0; j<1200;j++); // about 1 millisecond
	};
}

//! Wait for a packet to come, then immediately return.
void rxwait(){
  //Disable interrupts.
  RFTXRXIE=0;
  
  //idle a bit.
  RFST=RFST_SIDLE;
  while(MARCSTATE!=MARC_STATE_IDLE);
  
  //Begin to receive.
  RFST=RFST_SRX;
  while(MARCSTATE!=MARC_STATE_RX);
  
  //Incoming!  Return to let the jammer handle things.
  
}

//! Reflexively jam on the present channel by responding to a signal with a carrier wave.
void main(){
  unsigned char threshold=packet[0], i=0, rssi=0;;
  
  
  //Disable interrupts.
  RFTXRXIE=0;
  
  //idle a bit.
  //RFST=RFST_SIDLE;
  //while(MARCSTATE!=MARC_STATE_IDLE);

  while(1){
    
    rxwait();
    
    //idle a bit.
    RFST=RFST_SIDLE;
    while(MARCSTATE!=MARC_STATE_IDLE);
    
    SYNC1=0xAA;
    SYNC0=0xAA;
    
    //Transmit carrier for 10ms
    RFST=RFST_STX;
    while(MARCSTATE!=MARC_STATE_TX);
    sleepMillis(20);
    
    //Carrier will clear when the loop continue,
    //but we can HALT to give the host a chance to take over.
    HALT;
  }  
  RFST = RFST_SIDLE; //End transmit.
  
  HALT;
}
