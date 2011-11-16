/*! \file i2c.c
  \author Travis Goodspeed
  \brief I2C Master  
*/


//Higher level left to client application.

//Based upon a neighborly example at
//http://codinglab.blogspot.com/2008/10/i2c-on-avr-using-bit-banging.html

#include "platform.h"
#include "command.h"
#include "i2c.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>


//Pins and I/O
#include <jtag.h>

//! Handles an i2c command.
void i2c_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len);

// define the i2c app's app_t
app_t const i2c_app = {

	/* app number */
	I2C_APP,

	/* handle fn */
	i2c_handle_fn,

	/* name */
	"I2C",

	/* desc */
	"\tThe I2C app implements the i2c bus protocol thus\n"
	"\tturning your GoodFET into a USB-to-i2c adapter.\n"
};

#define I2CDELAY(x) delay(x<<4)


//2xx only, need 1xx compat code
#if (board == tilaunchpad)
// P3.1 SDA
// P3.3 SCL
#define SDA (1<<1)
#define SCL (1<<3)

#define CLRSDA P3OUT&=~SDA
#define SETSDA P3OUT|=SDA
#define CLRSCL P3OUT&=~SCL
#define SETSCL P3OUT|=SCL

#define READSDA (P3IN&SDA?1:0)
#define SDAINPUT P3DIR&=~SDA
#define SDAOUTPUT P3DIR|=SDA
#define SCLINPUT P3DIR&=~SCL
#define SCLOUTPUT P3DIR|=SCL
#define SETBOTH P3OUT|=(SDA|SCL)

#else

#define SDA TDI
#define SCL TDO

#define CLRSDA P5OUT&=~SDA
#define SETSDA P5OUT|=SDA
#define CLRSCL P5OUT&=~SCL
#define SETSCL P5OUT|=SCL

#define READSDA (P5IN&SDA?1:0)
#define SETBOTH P5OUT|=(SDA|SCL)
#endif

#define I2C_DATA_HI() SETSDA
#define I2C_DATA_LO() CLRSDA

#define I2C_CLOCK_HI() SETSCL
#define I2C_CLOCK_LO() CLRSCL

//#warning "Using internal resistors.  Won't work on 161x devices."

//! Inits bitbanging port, must be called before using the functions below
void I2C_Init()
{
  
  //Clear SDA and SCL.
  //Direction, not value, is used to set the value.
  //(Pull-up or 0.)
  
#if (platform == tilaunchpad)
  SDAOUTPUT;
  SCLOUTPUT;
#else
  P5DIR|=(SDA|SCL);
#endif
  //P5REN|=SDA|SCL;
  
  
  I2C_CLOCK_HI();
  I2C_DATA_HI();

  I2CDELAY(1);
}

#if (platform == tilaunchpad)
void I2C_Exit()
{
  SDAINPUT;
  SCLINPUT;
}
#endif

//! Write an I2C bit.
void I2C_WriteBit( unsigned char c )
{
  if(c>0)
    I2C_DATA_HI();
  else
    I2C_DATA_LO();

  I2C_CLOCK_HI();
  I2CDELAY(1);

  I2C_CLOCK_LO();
  I2CDELAY(1);

  if(c>0)
    I2C_DATA_LO();

  I2CDELAY(1);
}

//! Read an I2C bit.
unsigned char I2C_ReadBit()
{
  I2C_DATA_HI();

  I2C_CLOCK_HI();
  SDAINPUT;
  I2CDELAY(1);
  
  unsigned char c = READSDA;

  I2C_CLOCK_LO();
  I2CDELAY(1);
  SDAOUTPUT;

  return c;
}


//! Send a START Condition
void I2C_Start()
{
  // set both to high at the same time
  SETBOTH;
  I2CDELAY(1);
  
  I2C_DATA_LO();
  I2CDELAY(1);
  
  I2C_CLOCK_LO();
  I2CDELAY(1);
}

//! Send a STOP Condition
void I2C_Stop()
{
  I2C_CLOCK_HI();
  I2CDELAY(1);

  I2C_DATA_HI();
  I2CDELAY(1);
}

//! write a byte to the I2C slave device
unsigned char I2C_Write( unsigned char c )
{
  char i;
  for (i=0;i<8;i++){
    I2C_WriteBit( c & 0x80 );
    c<<=1;
  }
  
  return I2C_ReadBit();
}


//! read a byte from the I2C slave device
unsigned char I2C_Read( unsigned char ack )
{
  unsigned char res = 0;
  char i;
  
  for (i=0;i<8;i++){
    res <<= 1;
    res |= I2C_ReadBit();  
  }
  
  if( ack > 0)
    I2C_WriteBit(0);
  else
    I2C_WriteBit(1);
  
  I2CDELAY(1);
  
  return res;
}


//! Handles an i2c command.
void i2c_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len)
{
	unsigned char i;
	unsigned long l;
	switch(verb)
	{

	case PEEK:
		break;
	case POKE:
		break;

	case READ:
		l = len;
		if(l > 0)					//optional parameter of length
			l=cmddata[0];
		if(!l)						//default value of 1
			l=1;
		for(i = 0; i < l; i++)
			cmddata[i]=I2C_Read(1);	//Always acknowledge
		txdata(app,verb,l);
		break;
	case WRITE:
		cmddata[0]=0;
		for(i=0;i<len;i++)
			cmddata[0]+=I2C_Write(cmddata[i]);
		txdata(app,verb,1);
		break;
	case START:
		I2C_Start();
		txdata(app,verb,0);
		break;
	case STOP:
		I2C_Stop();
		txdata(app,verb,0);
		break;
	case SETUP:
		I2C_Init();
		txdata(app,verb,0);
		break;
	}
}
