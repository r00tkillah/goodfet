//! MSP430F1612/1611 clock and I/O definitions

#include "platform.h"

//! Receive a byte.
unsigned char serial0_rx(){
  return 0;
}

//! Receive a byte.
unsigned char serial1_rx(){
  return 0;
}

//! Transmit a byte.
void serial0_tx(unsigned char x){
}

//! Transmit a byte on the second UART.
void serial1_tx(unsigned char x){
}

//! Set the baud rate.
void setbaud0(unsigned char rate){
  
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


void msp430_init_uart0(){
}


void msp430_init_uart1(){
}



//! Initialization is correct.
void msp430_init_dco_done(){
  //Nothing to do for the 1612.
}


void msp430_init_dco() {

}

