/*! \file stm32f407.h
  \author Travis Goodspeed
  \brief STM32F407 port definitions.
*/

#include "platform.h"

#include "stm32f4xx.h"
//#include "stm322xg_eval.h"
#include <stm32f4xx_gpio.h>
#include <stm32f4xx_rcc.h>
#include <stm32f4xx_usart.h>
#include "stm32f4_discovery.h"

void ioinit(){
  GPIO_InitTypeDef  GPIO_InitStructure;
  
  /* GPIOD Periph clock enable */
  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOD, ENABLE);

  /* Configure PD12, PD13, PD14 and PD15 in output pushpull mode */
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_12 | GPIO_Pin_13| GPIO_Pin_14| GPIO_Pin_15;
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz;
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL;
  GPIO_Init(GPIOD, &GPIO_InitStructure);
}

void stmdelay(){
  //IO so it doesn't get swapped out.
  __IO uint32_t count=   0x1000;   // >1kbit/s
  //__IO uint32_t count= 0x100000; // 5 bits per second, for testing
  while(count--);
}
void ledon(){
  GPIO_SetBits(GPIOD, GPIO_Pin_14);
}
void ledoff(){
  GPIO_ResetBits(GPIOD, GPIO_Pin_14);
}
void clkon(){
  GPIO_SetBits(GPIOD, GPIO_Pin_12);
}
void clkoff(){
  GPIO_ResetBits(GPIOD, GPIO_Pin_12);
}

void spibit(int one){
  if(one) ledon();
  else    ledoff();
  clkon();
  stmdelay();
  clkoff();
  stmdelay();
}

void spiword(uint32_t word){
  int i=32;
  while(i--){
    //morsebit(word&1);
    //manchesterbit(word&1);
    spibit(word&1);
    word=(word>>1);
  }
}
void spibyte(uint8_t word){
  int i=8;
  while(i--){
    //morsebit(word&1);
    //manchesterbit(word&1);
    spibit(word&1);
    word=(word>>1);
  }
}



//! Count the length of a string.
uint32_t strlen(const char *s){
  int i=0;
  while(s[i++]);
  return i-1;
}


//! Initialize the USART
void usartinit(){
  USART_InitTypeDef USART_InitStructure;
  GPIO_InitTypeDef GPIO_InitStructure;
  USART_ClockInitTypeDef USART_ClockInitStruct;
  
  /* Enable GPIOA and USART1 clock */
  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
  
  //USART1 and USART6, other in APB1
  RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1, ENABLE);
  
  RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1, ENABLE);
  /* A 9 to USART1_Tx
   * A10 to USART1_Rx
   * A11 to USART1_CTS
   * A12 to USART1_RTS 
   */
  GPIO_PinAFConfig(GPIOA, GPIO_PinSource9, GPIO_AF_USART1);
  GPIO_PinAFConfig(GPIOA, GPIO_PinSource10, GPIO_AF_USART1);
  GPIO_PinAFConfig(GPIOA, GPIO_PinSource11, GPIO_AF_USART1);
  GPIO_PinAFConfig(GPIOA, GPIO_PinSource12, GPIO_AF_USART1);
 
  /* Configure USART Tx and Rx as alternate function push-pull */
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF;
  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP;
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9 | GPIO_Pin_10 | GPIO_Pin_11 | GPIO_Pin_12;
  GPIO_Init(GPIOA, &GPIO_InitStructure);
  
  
  USART_StructInit(&USART_InitStructure);
  USART_InitStructure.USART_BaudRate = 9600;
  USART_InitStructure.USART_WordLength = USART_WordLength_8b;
  USART_InitStructure.USART_StopBits = USART_StopBits_1;
  USART_InitStructure.USART_Parity = USART_Parity_No;
  USART_InitStructure.USART_HardwareFlowControl =  USART_HardwareFlowControl_None;
  USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
  USART_Init(USART1, &USART_InitStructure);
  
  
  USART_ClockStructInit(&USART_ClockInitStruct);
  USART_ClockInit(USART1,&USART_ClockInitStruct);
  
  USART_Cmd(USART1, ENABLE);
}


//! Initialize the STM32F4xx ports and USB.
void stm32f4xx_init(){
  int i=20;
  
  //SystemInit();
  usartinit();
  ioinit();
  
  ledoff();
  clkoff();
  
  return;
}

//! Receive a byte.
unsigned char serial0_rx(){
}

//! Receive a byte.
unsigned char serial1_rx(){
}

//! Transmit a byte.
void serial0_tx(unsigned char x){
  USART_SendData(USART1, (uint16_t) x);
  //while(USART_GetFlagStatus(USART1, USART_FLAG_TXE) == RESET);
  
  spibyte(x);
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
