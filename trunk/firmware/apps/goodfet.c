//GOODFET Echo test.


#include "platform.h"
#include "command.h"
#include "apps.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>


//LED on P1.0
//IO on P5

//! Initialize registers and all that jazz.
void init(){
  volatile unsigned int i;
  WDTCTL = WDTPW + WDTHOLD;                 // Stop watchdog timer
  
  //LED and TX OUT
  PLEDDIR |= PLEDPIN;
  
  msp430_init_dco();
  msp430_init_uart();
  
  //Enable Interrupts.
  //eint();
}

//! Handle a command.
void handle(unsigned char app,
	    unsigned char verb,
	    unsigned char len){
  switch(app){
  case MONITOR:
    monitorhandle(app,verb,len);
    break;
  default:
    txdata(app,NOK,0);
  }
}

//! Main loop.
int main(void)
{
  volatile unsigned int i;
  unsigned char app, verb, len;
  
  init();
  
  //Command loop.  There's no end!
  while(1){
    //Ready
    txdata(MONITOR,OK,0);
    
    //Magic 3
    app=serial_rx();
    verb=serial_rx();
    len=serial_rx();
    //Read data, if any
    for(i=0;i<len;i++){
      cmddata[i]=serial_rx();
    }
    handle(app,verb,len);
  }
    
  //while(1) serial_tx(serial_rx());
  while(1) serial_tx(serial_rx());
  
  while(1){
    i = 10000;
    while(i--);
    
    PLEDOUT^=PLEDPIN;  // Blink
  }
}

