//GOODFET Blinker

//1611 is preferred, but 1612 accepted

#include <signal.h>
#include <io.h>
#include <iomacros.h>

//LED on P1.0
//IO on P5

//! Initialize registers and all that jazz.
void init(){
  WDTCTL = WDTPW + WDTHOLD;                 // Stop watchdog timer
  
  //LED and TX OUT
  P1DIR = 0x03;
  
  //Enable Interrupts.
  //eint();
}

//! Main loop.
int main(void)
{
  volatile unsigned int i;
  init();
  
  while(1){
    i = 10000;
    while(i--);
    
    P1OUT^=1;                                   // Blink
  }
}

