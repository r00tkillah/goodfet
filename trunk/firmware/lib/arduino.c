/*! \file arduino.c
  \author Travis Goodspeed
  \brief Arduino platform support.
*/

#include "platform.h"
#ifdef ARDUINO

#include <util/delay.h>

//! Arduino setup code.
void arduino_init(){
  /* set PORTB for output*/
  DDRB = 0xFF;
  
  /*
  while (1)
    {
    //LED on
      PORTB = 0x20;

      _delay_ms(1000);

      //LED off
      PORTB = 0x00;

      _delay_ms(1000);
    }
*/
}

#endif
