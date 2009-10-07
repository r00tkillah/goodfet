/*! \file avr.h
  \author Travis Goodspeed
  \brief AVR SPI Programmer
*/

#include "spi.h"

//! Setup the AVR pins.
void avrsetup();

//! Initialized an attached AVR.
void avrconnect();

//! Enable AVR programming mode.
void avr_prgen();
//! Read AVR device code.
u8 avr_sig(u8 i);


//Command codes.
//! Performa  chip erase.
#define AVR_ERASE 0xF0
//! Fetch RDY/!BSY byte.
#define AVR_RDYBSY 0xF1

//! Read Program Memory
#define AVR_PEEKPGM 0x80
//! Read EEPROM
#define AVR_PEEKEEPROM 0x81
//! Read lock bits.
#define AVR_PEEKLOCK 0x82
//! Read signature.
#define AVR_PEEKSIG 0x83
//! Read fuse bits.
#define AVR_READFUSES 0x84
//! Read calibration byte.
#define AVR_READCAL 0x85
