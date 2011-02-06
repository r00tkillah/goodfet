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

#define RESET 0x80      // not a real app -- causes firmware to reset
#define DEBUGAPP 0xFF

//! Initialize registers and all that jazz.
void init()
{
#ifdef DAC12IR
	int i;
#endif

	WDTCTL = WDTPW + WDTHOLD;					// Stop watchdog timer

	//LED out and on.
	PLEDDIR |= PLEDPIN;
	PLEDOUT &= ~PLEDPIN;


	/* P5.0 out and low; this is chosen for the PIC app (in which P5.0
	 is !MCLR) to ensure that an attached PIC chip, if present, is
	 immediately driven to reset state. A brief explanation of why this
	 is important follows.

	At least dsPIC33F and PIC24H --and very likely other 16-bit PIC
	families-- draw a large amount of current when running, especially
	when using a fast clock: from 60 mA up to approx. 90 mA.  If the
	PIC target begins to run before the client can request a new ICSP
	session, which requires much less current (e.g., less than 2 mA),
	then the MSP430 chip on the GoodFET will fail to start and the FTDI
	may have trouble communicating with the client.	The latter likely
	relates to the FTDI on-chip 3V3 regulator being specified up to
	only 50 mA. */


	//P5REN &= ~BIT0; //DO NOT UNCOMMENT.  Breaks GF1x support.

	//This will have to be cut soon.	Use pulling resistors instead.
	/*
	P5DIR |= BIT0;
	P5OUT &= ~BIT0;
	*/

	//Setup clocks, unique to each '430.
	msp430_init_dco();
	msp430_init_uart();

	//DAC should be at full voltage if it exists.
#ifdef DAC12IR
	//glitchvoltages(0xfff,0xfff);
	ADC12CTL0 = REF2_5V + REFON;					// Internal 2.5V ref on
	for(i=0;i!=0xFFFF;i++) asm("nop");
	DAC12_0CTL = DAC12IR + DAC12AMP_5 + DAC12ENC; // Int ref gain 1
	DAC12_0DAT = 0xFFF; //Max voltage 0xfff
	DAC12_1CTL = DAC12IR + DAC12AMP_5 + DAC12ENC; // Int ref gain 1
	DAC12_1DAT = 0x000; //Min voltage 0x000
#endif

	/** FIXME
	  
	  This part is really ugly.  GSEL (P5.7) must be high to select
	  normal voltage, but a lot of applications light to swing it low
	  to be a nuissance.  To get around this, we assume that anyone
	  with a glitching FET will also have a DAC, then we set that DAC
	  to a high voltage.
	  
	  At some point, each target must be sanitized to show that it
	  doesn't clear P5OUT or P5DIR.
	*/
	P5DIR|=BIT7; P5OUT=BIT7; //Normal Supply
	//P5DIR&=~BIT7; //Glitch Supply

	//Enable Interrupts.
	//eint();
	
	#ifdef INITPLATFORM
	INITPLATFORM;
	#endif
}


//! Handle a command.
void handle(uint8_t const app,
	    uint8_t const verb,
	    uint32_t const len){
  int i;

  //debugstr("GoodFET");
  PLEDOUT&=~PLEDPIN;

  // find the app and call the handle fn
  for(i = 0; i < num_apps; i++){
    if(apps[i]->app == app){
      // call the app's handle fn
      (*(apps[i]->handle))(app, verb, len);
      
      // exit early
      return;
    }
  }

  // if we get here, then the desired app is not copiled in 
  // this firmware
  debugstr("App missing.");
  debughex(app);
  txdata(app, NOK, 0);
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
	while(1)
	{
		//Magic 3
		app = serial_rx();

		// If the app is the reset byte (0x80) increment and loop
		if (app == RESET)
		{
			reset_count++;

			if (reset_count > 4) 
			{
				// We could trigger the WDT with either:
				// WDTCTL = 0;
				// or
				// WDTCTL = WDTPW + WDTCNTCL + WDTSSEL + 0x00;
				// but instead we'll jump to our reboot function pointer
				(*reboot_function)();
			}

			continue;
		} 
		else 
		{
			reset_count = 0;
		}

		verb = serial_rx();
		//len=serial_rx();
		len = rxword();

		//Read data, looking for buffer overflow.y
		if(len <= CMDDATALEN)
		{
			for(i = 0; i < len; i++)
			{
				cmddata[i] = serial_rx();
			}

			handle(app,verb,len);
		}
		else
		{
			//Listen to the blaberring.
			for(i = 0; i < len; i++)
				serial_rx();

			//Reply with an error.
			debugstr("Buffer length exceeded.");
			txdata(MONITOR,NOK,0);
		}
	}
}

