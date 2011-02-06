/*! \file spi.h
  \author Travis Goodspeed
  \brief Definitions for the SPI application.
*/

#ifndef SPI_H
#define SPI_H

#include "app.h"

#define SPI 0x01

//Pins and I/O
#define MOSI BIT1
#define MISO BIT2
#define SCK  BIT3

#define SETMOSI SPIOUT|=MOSI
#define CLRMOSI SPIOUT&=~MOSI
#define SETCLK SPIOUT|=SCK
#define CLRCLK SPIOUT&=~SCK
#define READMISO (SPIIN&MISO?1:0)

//FIXME this should be defined by the platform.
#define SETTST P4OUT|=TST
#define CLRTST P4OUT&=~TST
#define SETRST P2OUT|=RST
#define CLRRST P2OUT&=~RST

//! Set up the pins for SPI mode.
void spisetup();

//! Read and write an SPI byte.
unsigned char spitrans8(unsigned char byte);

//! Read a block to a buffer.
void spiflash_peekblock(unsigned long adr,
			unsigned char *buf,
			unsigned int len);


//! Write many blocks to the SPI Flash.
void spiflash_pokeblocks(unsigned long adr,
			 unsigned char *buf,
			 unsigned int len);


//! Enable SPI writing
void spiflash_wrten();

//! Read and write an SPI byte.
unsigned char spitrans8(unsigned char byte);
//! Grab the SPI flash status byte.
unsigned char spiflash_status();
//! Erase a sector.
void spiflash_erasesector(unsigned long adr);

extern app_t const spi_app;

#endif
