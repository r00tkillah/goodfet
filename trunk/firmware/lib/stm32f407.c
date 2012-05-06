/*! \file stm32f407.h
  \author Travis Goodspeed
  \brief STM32F407 port definitions.
*/

#include "platform.h"

#include "stm32f4xx.h"
//#include "stm322xg_eval.h"
#include <stm32f4xx_gpio.h>
#include <stm32f4xx_rcc.h>
#include <stm32f4xx_rcc.h>
//#include "stm32f4_discovery.h"


void ioinit(){
  GPIO_InitTypeDef  GPIO_InitStructure;
  
  /* GPIOD Periph clock enable */
  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOD, ENABLE);

  /* Configure PD12, PD13, PD14 and PD15 in output pushpull mode */
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_12 | GPIO_Pin_13| GPIO_Pin_14| GPIO_Pin_15;
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_100MHz;
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL;
  GPIO_Init(GPIOD, &GPIO_InitStructure);
}


void ledon(){
  //GPIOG->BSRRL=GPIO_Pin_14;
  GPIO_ResetBits(GPIOD, GPIO_Pin_14);
}
void ledoff(){
  //GPIOG->BSRRH=GPIO_Pin_14;
  GPIO_SetBits(GPIOD, GPIO_Pin_14);
}


//! Count the length of a string.
uint32_t strlen(const char *s){
  return 0;
}

//! Initialize the STM32F4xx ports and USB.
void stm32f4xx_init(){
  SystemInit();
  ioinit();
  while(1){
    ledon();
    delay(0x1000);
    ledoff();
    delay(0x1000);
  }
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
