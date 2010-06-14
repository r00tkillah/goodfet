/*! \file spi.h
  \author Travis Goodspeed
  \brief Definitions for the SPI application.
*/


//Pins and I/O
//#define SS BIT0
#define MOSI BIT1
#define MISO BIT2
#define SCK  BIT3

#define SETMOSI P5OUT|=MOSI
#define CLRMOSI P5OUT&=~MOSI
#define SETCLK P5OUT|=SCK
#define CLRCLK P5OUT&=~SCK
#define READMISO (P5IN&MISO?1:0)

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
