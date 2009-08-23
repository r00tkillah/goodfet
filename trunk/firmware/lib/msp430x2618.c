//! MSP430F2618 clock and I/O definitions

// Ought to be portable to other 2xx chips.
// 2274 looks particularly appealing.

#include "platform.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>


//! Receive a byte.
unsigned char serial_rx(){
  char c;
  
  while(!(IFG2&UCA0RXIFG));//wait for a byte
  c = UCA0RXBUF;
  IFG2&=~UCA0RXIFG;
  
  //UCA0CTL1 &= ~UCA0RXSE;
  return c;
}

//! Receive a byte.
unsigned char serial1_rx(){
  //TODO
}


//! Transmit a byte.
void serial_tx(unsigned char x){
  while ((IFG2 & UCA0TXIFG) == 0); //loop unti lbuffer is free
  UCA0TXBUF = x;	/* send the character */
  while(!(IFG2 & UCA0TXIFG));
}

//! Transmit a byte on the second UART.
void serial1_tx(unsigned char x){
}

//! Set the baud rate.
void setbaud(unsigned char rate){
  
  //http://mspgcc.sourceforge.net/baudrate.html
  switch(rate){
  case 1://9600 baud
    
    break;
  case 2://19200 baud
    
    break;
  case 3://38400 baud
    
    break;
  case 4://57600 baud
    
    break;
  default:
  case 5://115200 baud
    
    break;
  }
}

//! Set the baud rate of the second uart.
void setbaud1(unsigned char rate){
  
  //http://mspgcc.sourceforge.net/baudrate.html
  switch(rate){
  case 1://9600 baud
    
    break;
  case 2://19200 baud
    
    break;
  case 3://38400 baud
    
    break;
  case 4://57600 baud
    
    break;
  default:
  case 5://115200 baud
    
    break;
  }
}


//host.h says 0x2B for DCO=4.9MHZ
//Divide by four for accuracy.

//19200
#define BAUD0EN 0x41
#define BAUD1EN 0x03


void msp430_init_uart(){
  // Serial on P3.4, P3.5
  P3SEL |= BIT4 + BIT5;
  P3DIR |= BIT4;
  
  //UCA0CTL1 |= UCSWRST;                    /* disable UART */

  UCA0CTL0 = 0x00;
  //UCA0CTL0 |= UCMSB ;
  UCA0CTL1 |= UCSSEL_2;                     // SMCLK
  UCA0BR0 = BAUD0EN;                        // 115200
  UCA0BR1 = BAUD1EN;
  UCA0MCTL = 0;                             // Modulation UCBRSx = 5
  UCA0CTL1 &= ~UCSWRST;                     // **Initialize USCI state machine**
  
}


void msp430_init_dco() {
  BCSCTL1 = CALBC1_16MHZ;
  DCOCTL = CALDCO_16MHZ;
  
  return;
}

