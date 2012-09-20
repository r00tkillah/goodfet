/*! \file ccspi.h
  \author Travis Goodspeed
  \brief Constants for CCSPI Driver
*/

#ifndef CCSPI_H
#define CCSPI_H

#include "app.h"

#define CCSPI 0x51

//Chipcon SPI Commands

//Grab a packet, if one is available.
#define CCSPI_RX 0x80
//Grab and decrypt a packet, if one is available.
#define CCSPI_RXDEC 0x90
//Send a packet.
#define CCSPI_TX 0x81
//Flush RX
#define CCSPI_RX_FLUSH 0x82
//Flush TX
#define CCSPI_TX_FLUSH 0x83
//Reflexive jam.
#define CCSPI_REFLEX 0xA0
//Reflexive jam that sends a forged ACK frame if one was requested
#define CCSPI_REFLEX_AUTOACK 0xA1


//Bit fields for command word.
#define CCSPI_R_REGISTER 0
#define CCSPI_W_REGISTER BIT7
#define CCSPI_R_RAM BIT6
#define CCSPI_W_RAM (BIT6|BIT7)



//Register definitions might go here, at least for buffers.
#define CCSPI_MANFIDL 0x1E
#define CCSPI_MANFIDH 0x1F
#define CCSPI_TXFIFO  0x3E
#define CCSPI_RXFIFO  0x3F
#define CCSPI_SFLUSHRX 0x08
#define CCSPI_SFLUSHTX 0x09
#define CCSPI_SRXDEC 0x0C
#define CCSPI_STXENC 0x0D

extern app_t const ccspi_app;

#endif // CCSPI_H

