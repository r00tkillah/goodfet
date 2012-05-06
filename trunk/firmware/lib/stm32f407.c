/*! \file stm32f407.h
  \author Travis Goodspeed
  \brief STM32F407 port definitions.
*/

#include "platform.h"


//! Count the length of a string.
uint32_t strlen(const char *s){
  return 0;
}

//! Initialize the STM32F4xx ports and USB.
void stm32f4xx_init(){
  
}

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


//Declarations
void nmi_handler(void);
void hardfault_handler(void);
int main(void);

//From min.s
void Reset_Handler(void);



// Define the vector table
unsigned int * myvectors[50] 
   __attribute__ ((section("vectors")))= {
   	(unsigned int *)	0x20000800,	        // stack pointer
   	(unsigned int *) 	Reset_Handler,		        // code entry point
   	(unsigned int *)	main,		// NMI handler (not really)
   	(unsigned int *)	main,	// hard fault handler (let's hope not)	
};
