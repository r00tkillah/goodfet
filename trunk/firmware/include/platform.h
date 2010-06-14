/*! \file platform.h
  \author Travis Goodspeed
  \brief Port and baud rate definitions.
  
  The functions specified here are defined in the platform
  definition file, such as msp430x1612.c or msp430x2618.c.
*/

#include "config.h"

#include "gfports.h"

#ifdef telosb
//TelosB uses second serial port.
#define serial_tx serial1_tx
#define serial_rx serial1_rx
#define setbaud setbaud1
#define msp430_init_uart msp430_init_uart1
#else
//Other targets use first.
#define serial_tx serial0_tx
#define serial_rx serial0_rx
#define setbaud setbaud0
#define msp430_init_uart msp430_init_uart0
#endif

unsigned char serial0_rx();
void serial0_tx(unsigned char);

unsigned char serial1_rx();
void serial1_tx(unsigned char);

void setbaud0(unsigned char);
void setbaud1(unsigned char);

//! Initialize the UART
void msp430_init_uart0();
//! Initialize the UART
void msp430_init_uart1();

//! Initialize the DCO Clock
void msp430_init_dco();
//! Called by monitor() when the DCO is correct and communication established.
void msp430_init_dco_done();

