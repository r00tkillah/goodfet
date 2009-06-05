//! MSP430F1612/1611 clock and I/O definitions

#include "platform.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>


//! Receive a byte.
unsigned char serial_rx(){
  char c;
  
  while(!(IFG1&URXIFG0));//wait for a byte
  c = RXBUF0;
  IFG1&=~URXIFG0;
  U0TCTL &= ~URXSE;
  
  return c;
}
//! Transmit a byte.
void serial_tx(unsigned char x){
  while ((IFG1 & UTXIFG0) == 0); //loop until buffer is free
  TXBUF0 = x;
}


void msp430_init_uart(){
  
  /* RS232 */
  
  P3SEL |= BIT4|BIT5;                        // P3.4,5 = USART0 TXD/RXD
  P3DIR |= BIT4;
  
  
  UCTL0 = SWRST | CHAR;                 /* 8-bit character, UART mode */
  
  
  UTCTL0 = SSEL1;                       /* UCLK = MCLK */

  //http://mspgcc.sourceforge.net/baudrate.html
  //9600 baud
  UBR00=0x00; UBR10=0x01; UMCTL0=0x00;
  
  ME1 &= ~USPIE0;			/* USART1 SPI module disable */
  ME1 |= (UTXE0 | URXE0);               /* Enable USART1 TXD/RXD */

  UCTL0 &= ~SWRST;

  /* XXX Clear pending interrupts before enable!!! */
  U0TCTL |= URXSE;

  //IE1 |= URXIE1;                        /* Enable USART1 RX interrupt  */
}


void msp430_init_dco() {
    /* This code taken from the FU Berlin sources and reformatted. */
#define MSP430_CPU_SPEED 2457600UL
#define DELTA    ((MSP430_CPU_SPEED) / (32768 / 8))
  unsigned int compare, oldcapture = 0;
  unsigned int i;
  
  WDTCTL = WDTPW + WDTHOLD; //stop WDT

  BCSCTL1 = 0xa4; /* ACLK is devided by 4. RSEL=6 no division for MCLK
		     and SSMCLK. XT2 is off. */

  BCSCTL2 = 0x00; /* Init FLL to desired frequency using the 32762Hz
		     crystal DCO frquenzy = 2,4576 MHz  */

  BCSCTL1 |= DIVA1 + DIVA0;             /* ACLK = LFXT1CLK/8 */
  for(i = 0xffff; i > 0; i--) {         /* Delay for XTAL to settle */
    asm("nop");
  }

  CCTL2 = CCIS0 + CM0 + CAP;            // Define CCR2, CAP, ACLK
  TACTL = TASSEL1 + TACLR + MC1;        // SMCLK, continous mode


  while(1) {

    while((CCTL2 & CCIFG) != CCIFG);    /* Wait until capture occured! */
    CCTL2 &= ~CCIFG;                    /* Capture occured, clear flag */
    compare = CCR2;                     /* Get current captured SMCLK */
    compare = compare - oldcapture;     /* SMCLK difference */
    oldcapture = CCR2;                  /* Save current captured SMCLK */

    if(DELTA == compare) {
      break;                            /* if equal, leave "while(1)" */
    } else if(DELTA < compare) {        /* DCO is too fast, slow it down */
      DCOCTL--;
      if(DCOCTL == 0xFF) {              /* Did DCO role under? */
	BCSCTL1--;
      }
    } else {                            /* -> Select next lower RSEL */
      DCOCTL++;
      if(DCOCTL == 0x00) {              /* Did DCO role over? */
	BCSCTL1++;
      }
                                        /* -> Select next higher RSEL  */
    }
  }

  CCTL2 = 0;                            /* Stop CCR2 function */
  TACTL = 0;                            /* Stop Timer_A */

  BCSCTL1 &= ~(DIVA1 + DIVA0);          /* remove /8 divisor from ACLK again */
}
