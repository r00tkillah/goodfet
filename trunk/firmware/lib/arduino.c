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
  
  avr_init_uart0();
}

#endif
