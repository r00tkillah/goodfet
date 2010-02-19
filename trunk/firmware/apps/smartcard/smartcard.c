/*! \file smartcard.c
  \author Travis Goodspeed
  \brief Smartcard and SIM application.
  
  This module allows for communication with smart cards and SIM cards.
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"

//! Handles a monitor command.
int smartcardhandle(unsigned char app,
	      unsigned char verb,
	      unsigned int len){
  switch(verb){
  case START:
    debugstr("Unable to start smart card.");
    break;
  case STOP:
  default:
    debugstr("Unknown smartcard verb.");
    txdata(app,NOK,0);
  }
}
