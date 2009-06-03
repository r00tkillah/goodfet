//! Command handling functions.

//! Global data buffer.
extern unsigned char cmddata[256];
#define cmddataword ((unsigned int*) cmddata)
#define memorybyte ((unsigned char*) 0)

// Command prefixes
#define READ  0x00
#define WRITE 0x01
#define PEEK  0x02
#define POKE  0x03
#define NOK   0x7E
#define OK    0x7F

//!Handle a command.  Defined in goodfet.c
void handle(unsigned char app,unsigned char verb,unsigned  char len);

//!Transmit data.
void txdata(unsigned char app,
	    unsigned char verb,
	    unsigned char len);
