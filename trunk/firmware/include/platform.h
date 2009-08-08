//! \file platform.h

unsigned char serial_rx();
void serial_tx(unsigned char);

unsigned char serial1_rx();
void serial1_tx(unsigned char);

void setbaud(unsigned char);
void setbaud1(unsigned char);

//! Initialize the UART
void msp430_init_uart();
//! Initialize the DCO Clock
void msp430_init_dco();

//LED on P1.0
#define PLEDOUT P1OUT
#define PLEDDIR P1DIR
#define PLEDPIN 0x1

