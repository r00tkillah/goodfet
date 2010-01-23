/*! \file goodfet.c
  \author Travis Goodspeed
  \brief Main module.
  
  This is the main module of the GoodFET, which calls the initialization
  routines and delegates commands to the various applications.
*/


#include "platform.h"
#include "command.h"
#include "apps.h"
#include "glitch.h"


//LED on P1.0
//IO on P5

//! Initialize registers and all that jazz.
void init(){
  WDTCTL = WDTPW + WDTHOLD;                 // Stop watchdog timer
  
  //LED out and on.
  PLEDDIR |= PLEDPIN;
  PLEDOUT &= ~PLEDPIN;
  
  //Setup clocks, unique to each '430.
  msp430_init_dco();
  msp430_init_uart();
  
  //DAC should be at full voltage if it exists.
  #ifdef DAC12IR
  glitchvoltages(0xfff,0xfff);
  #endif
  
  //Enable Interrupts.
  //eint();
}


//! Handle a command.
void handle(unsigned char app,
	    unsigned char verb,
	    unsigned long len){
  //debugstr("GoodFET");
  P1OUT&=~1;
  switch(app){
  case GLITCH:
    glitchhandle(app,verb,len);
    break;
  case MONITOR:
    monitorhandle(app,verb,len);
    break;
  case SPI:
    spihandle(app,verb,len);
    break;
  case AVR:
    avrhandle(app,verb,len);
    break;
  case I2CAPP:
    i2chandle(app,verb,len);
    break;
  case CHIPCON:
    cchandle(app,verb,len);
    break;
  case JTAG:
    jtaghandle(app,verb,len);
    break;
  case EJTAG:
    ejtaghandle(app,verb,len);
    break;
  case JTAG430: //Also JTAG430X, JTAG430X2
    jtag430x2handle(app,verb,len);
    break;
  default:
    if(pluginhandle){
      pluginhandle(app,verb,len);
    }else{
      debugstr("Plugin missing.");
      debughex(app);
      txdata(app,NOK,0);
    }
    break;
  }
}

//! Main loop.
int main(void)
{
  volatile unsigned int i;
  unsigned char app, verb;
  unsigned long len;
  // MSP reboot count for reset input & reboot function located at 0xFFFE
  volatile unsigned int reset_count = 0;
  void (*reboot_function)(void) = (void *) 0xFFFE;
  
  init();

  txstring(MONITOR,OK,"http://goodfet.sf.net/");
  
  
  //Command loop.  There's no end!
  while(1){
    //Magic 3
    app=serial_rx();

	// If the app is the reset byte (0x80) increment and loop
	if (app == 0x80) {
		reset_count++;

		if (reset_count > 4) {
			// We could trigger the WDT with either:
			// WDTCTL = 0;
			// or
			// WDTCTL = WDTPW + WDTCNTCL + WDTSSEL + 0x00;
			// but instead we'll jump to our reboot function pointer
			(*reboot_function)();
		}

		continue;
	} else {
		reset_count = 0;
	}

    verb=serial_rx();
    //len=serial_rx();
    len=rxword();
    
    //Read data, looking for buffer overflow.y
    if(len<=CMDDATALEN){
      for(i=0;i<len;i++){
	cmddata[i]=serial_rx();
      }
      handle(app,verb,len);
    }else{
      //Listen to the blaberring.
      for(i-0;i<len;i++)
	serial_rx();
      //Reply with an error.
      debugstr("Buffer length exceeded.");
      txdata(MONITOR,NOK,0);
    }
  }
}

