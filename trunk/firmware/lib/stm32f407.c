//! MSP430F2618 clock and I/O definitions

// Included by other 2xx ports, such as the 2274.

#include "platform.h"


//! Receive a byte.
unsigned char serial0_rx(){
}

//! Receive a byte.
unsigned char serial1_rx(){
}

//! Transmit a byte.
void serial0_tx(unsigned char x){
}
//! Transmit a byte.
void serial_tx_old(unsigned char x){
}

//! Transmit a byte on the second UART.
void serial1_tx(unsigned char x){

}

//! Set the baud rate.
void setbaud0(unsigned char rate){
  //Ignore this, as we'll be in USB.
}

//! Set the baud rate of the second uart.
void setbaud1(unsigned char rate){

}

void msp430_init_uart(){

}


//! Initialization is correct.
void msp430_init_dco_done(){
}

//! Initialize the MSP430 clock.
void msp430_init_dco() {
}

