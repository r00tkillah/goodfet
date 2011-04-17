//! MSP430F1612/1611 clock and I/O definitions

#include "platform.h"

#include <avr/io.h>
#include <util/delay.h>

//! Receive a byte.
unsigned char serial0_rx(){
  while( !(UCSR0A & (1 << RXC0)) );
  return UDR0;
}

//! Receive a byte.
unsigned char serial1_rx(){
  return 0;
}

//! Transmit a byte.
void serial0_tx(unsigned char x){
  while (!(UCSR0A & (1<<UDRE0)) );
  UDR0 = x;
}

//! Transmit a byte on the second UART.
void serial1_tx(unsigned char x){
}

//! Set the baud rate.
void setbaud0(unsigned char rate){
  //TODO support multiple rates.
  #define SPEED 9600
  
  
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
  
  uint16_t bittimer=( F_CPU / SPEED / 16 ) - 1;
  UBRR0H = (unsigned char) (bittimer >> 8);
  UBRR0L = (unsigned char) bittimer;
  
  
  /* set the framing to 8N1 */
  UCSR0C = (3 << UCSZ00);
  /* Engage! */
  UCSR0B = (1 << RXEN0) | (1 << TXEN0);
  return;
  
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


void msp430_init_uart0(){
}


void msp430_init_uart1(){
}



//! Initialization is correct.
void msp430_init_dco_done(){
  //Nothing to do for the AVR w/ xtal.
}


void msp430_init_dco() {
  //
}

