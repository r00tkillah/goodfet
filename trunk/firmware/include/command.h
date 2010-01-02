/*! \file command.h
  \author Travis Goodspeed
  \brief Command codes and buffers.
*/


//Types
#define u8 unsigned char
#define u16 unsigned int
#define u32 unsigned long


#ifdef msp430x2274
//256 bytes, plus overhead
//For chips with very little RAM.
#define CMDDATALEN 0x104
//#warning Very little RAM.
#endif

#ifndef CMDDATALEN
//512 bytes
#define CMDDATALEN 0x204
//4k
//#define CMDDATALEN 0x1004
#endif

//! Global data buffer.
extern unsigned char cmddata[CMDDATALEN];
extern unsigned char silent;

#define cmddataword ((unsigned int*) cmddata)
#define cmddatalong ((unsigned long*) cmddata)
#define memorybyte ((unsigned char*) 0)
#define memoryword ((unsigned int*) 0)

// Global Commands
#define READ  0x00
#define WRITE 0x01
#define PEEK  0x02
#define POKE  0x03
#define SETUP 0x10
#define START 0x20
#define STOP  0x21
#define NOK   0x7E
#define OK    0x7F

#define DEBUGSTR 0xFF

// Monitor Commands
#define MONITOR_CHANGE_BAUD 0x80
#define MONITOR_RAM_PATTERN 0x90
#define MONITOR_RAM_DEPTH 0x91

#define MONITOR_DIR 0xA0
#define MONITOR_OUT 0xA1
#define MONITOR_IN  0xA2

#define MONITOR_SILENT 0xB0

#define MONITOR_READBUF 0xC0
#define MONITOR_WRITEBUF 0xC1
#define MONITOR_SIZEBUF 0xC2




//SPI commands
#define SPI_JEDEC 0x80
#define SPI_ERASE 0x81

//OCT commands
#define OCT_CMP 0x90
#define OCT_RES 0x91

#define WEAKDEF __attribute__ ((weak))

//! Handle a plugin, weak-linked to error.
extern int pluginhandle(unsigned char app,
			unsigned char verb,
			unsigned int len)
  WEAKDEF;


//! Handle a command.  Defined in goodfet.c
void handle(unsigned char app,
	    unsigned char verb,
	    unsigned long len);
//! Transmit a header.
void txhead(unsigned char app,
	    unsigned char verb,
	    unsigned long len);
//! Transmit data.
void txdata(unsigned char app,
	    unsigned char verb,
	    unsigned long len);
//! Transmit a string.
void txstring(unsigned char app,
	      unsigned char verb,
	      const char *str);

//! Receive a long.
unsigned long rxlong();
//! Receive a word.
unsigned int rxword();

//! Transmit a long.
void txlong(unsigned long l);
//! Transmit a word.
void txword(unsigned int l);

//! Transmit a debug string.
void debugstr(const char *str);
//! brief Debug a hex word string.
void debughex(u16 v);

//! Delay for a count.
void delay(unsigned int count);
//! MSDelay
void msdelay(unsigned int ms);


void monitorhandle(unsigned char, unsigned char, unsigned long);
void spihandle(unsigned char, unsigned char, unsigned long);
void i2chandle(unsigned char, unsigned char, unsigned long) WEAKDEF;
void cchandle(unsigned char, unsigned char, unsigned long) WEAKDEF;
void jtaghandle(unsigned char, unsigned char, unsigned long);
void jtag430handle(unsigned char, unsigned char, unsigned long);
void jtag430x2handle(unsigned char app, unsigned char verb,
		     unsigned long len);
void avrhandle(unsigned char app,
	       unsigned char verb,
	       unsigned long len);  
