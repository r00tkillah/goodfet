/*! \file arduino.c
  \author Travis Goodspeed
  \brief Arduino platform support.
*/

#include "platform.h"

#include <util/delay.h>

#ifdef ARDUINO

//! Arduino setup code.
void arduino_init(){
  /* set PORTB for output*/
  DDRB = 0xFF;

  while (1)
    {
      /* set PORTB.6 high */
      PORTB = 0x20;

      _delay_ms(1000);

      /* set PORTB.6 low */
      PORTB = 0x00;

      _delay_ms(1000);
    }
}

#endif
