#include <cc1110.h>
#include "cc1110-ext.h"

char __xdata at 0xfe00 packet[256] ;

void sleepMillis(int ms) {
	int j;
	while (--ms > 0) { 
		for (j=0; j<1200;j++); // about 1 millisecond
	};
}

//! Reflexively jam on the present channel by responding to a signal with a carrier wave.
void main(){
  unsigned char threshold=packet[0], i=0, rssi=0;;
  
  
  //Disable interrupts.
  RFTXRXIE=0;
  
  //idle a bit.
  RFST=RFST_SIDLE;
  while(MARCSTATE!=MARC_STATE_IDLE);

  while(1){
    //Wait for the transmission.
    RFST=RFST_SRX;
    rssi=0;
    //Wait for RSSI to settle.
    sleepMillis(10);
    //Delay until the RSSI is above the threshold.
    while(rssi<threshold){
      rssi=RSSI^0x80;
      packet[0]=rssi;
    }
    
    //idle a bit.
    RFST=RFST_SIDLE;
    while(MARCSTATE!=MARC_STATE_IDLE);
    
    
    SYNC1=0xAA;
    SYNC0=0xAA;
    
    //Transmit carrier for 10ms
    RFST=RFST_STX;
    while(MARCSTATE!=MARC_STATE_TX);
    sleepMillis(10);
    
    //Carrier will clear when the loop continue,
    //but we can HALT to give the host a chance to take over.
    HALT;
  }  
  RFST = RFST_SIDLE; //End transmit.
  
  HALT;
}
