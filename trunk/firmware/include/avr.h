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
//! Erase an AVR device
void avr_erase();
//! Read lock bits.
u8 avr_lockbits();
//! Write lock bits.
void avr_setlock(u8 bits);

//! Read a byte of Flash
u8 avr_peekflash(u16 adr);

//! Read a byte of EEPROM.
u8 avr_peekeeprom(u16 adr);
//! Read a byte of EEPROM.
u8 avr_pokeeeprom(u16 adr, u8 val);

//! Is the AVR ready or busy?
u8 avr_isready();

//Command codes.
//! Performa  chip erase.
#define AVR_ERASE 0xF0
//! Fetch RDY/!BSY byte.
#define AVR_RDYBSY 0xF1

//! Read Program Memory
#define AVR_PEEKPGM 0x80
//! Read EEPROM
#define AVR_PEEKEEPROM 0x81
//! Write EEPROM
#define AVR_POKEEEPROM 0x91
//! Read lock bits.
#define AVR_PEEKLOCK 0x82
//! Write lock its.
#define AVR_POKELOCK 0x92
//! Read signature.
#define AVR_PEEKSIG 0x83
//! Read fuse bits.
#define AVR_READFUSES 0x84
//! Read calibration byte.
#define AVR_READCAL 0x85
