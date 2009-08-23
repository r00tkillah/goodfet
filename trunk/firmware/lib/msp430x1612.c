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

//! Receive a byte.
unsigned char serial1_rx(){
  char c;
  
  while(!(IFG2&URXIFG1));//wait for a byte
  c = RXBUF1;
  IFG2&=~URXIFG1;
  U1TCTL &= ~URXSE;
  
  return c;
}


//! Transmit a byte.
void serial_tx(unsigned char x){
  while ((IFG1 & UTXIFG0) == 0); //loop until buffer is free
  TXBUF0 = x;
}

//! Transmit a byte on the second UART.
void serial1_tx(unsigned char x){
  while ((IFG2 & UTXIFG1) == 0); //loop until buffer is free
  TXBUF1 = x;
}

//! Set the baud rate.
void setbaud(unsigned char rate){
  
  //http://mspgcc.sourceforge.net/baudrate.html
  switch(rate){
  case 1://9600 baud
    UBR00=0x7F; UBR10=0x01; UMCTL0=0x5B; /* uart0 3683400Hz 9599bps */
    break;
  case 2://19200 baud
    UBR00=0xBF; UBR10=0x00; UMCTL0=0xF7; /* uart0 3683400Hz 19194bps */
    break;
  case 3://38400 baud
    UBR00=0x5F; UBR10=0x00; UMCTL0=0xBF; /* uart0 3683400Hz 38408bps */
    break;
  case 4://57600 baud
    UBR00=0x40; UBR10=0x00; UMCTL0=0x00; /* uart0 3683400Hz 57553bps */
    break;
  default:
  case 5://115200 baud
    UBR00=0x20; UBR10=0x00; UMCTL0=0x00; /* uart0 3683400Hz 115106bps */
    break;
  }
}

//! Set the baud rate of the second uart.
void setbaud1(unsigned char rate){
  
  //http://mspgcc.sourceforge.net/baudrate.html
  switch(rate){
  case 1://9600 baud
    //    UBR01=0x7F; UBR11=0x01; UMCTL1=0x5B; /* uart0 3683400Hz 9599bps */
    break;
  case 2://19200 baud
    //UBR01=0xBF; UBR11=0x00; UMCTL1=0xF7; /* uart0 3683400Hz 19194bps */
    break;
  case 3://38400 baud
    //UBR01=0x5F; UBR11=0x00; UMCTL1=0xBF; /* uart0 3683400Hz 38408bps */
    break;
  case 4://57600 baud
    //UBR01=0x40; UBR11=0x00; UMCTL1=0x00; /* uart0 3683400Hz 57553bps */
    break;
  default:
  case 5://115200 baud
    //UBR01=0x20; UBR11=0x00; UMCTL1=0x00; /* uart0 3683400Hz 115106bps */
    break;
  }
}


void msp430_init_uart(){
}


void msp430_init_dco() {
}

