/*! \file atmel_radio.c
  \author bx forked from neighbor Travis Goodspeed
  \brief Atmel Radio Register Interface

*/

//Higher level left to client application.

#include "platform.h"
#include "command.h"
#include <stdlib.h> //added for itoa

#include "atmel_radio.h"
#include "spi.h"

//! Handles a Chipcon SPI command.
void atmel_radio_handle_fn( uint8_t const app,
                            uint8_t const verb,
                            uint32_t const len);

// define the atmel_radio app's app_t
app_t const atmel_radio_app = {

  /* app number */
  ATMEL_RADIO,

  /* handle fn */
  atmel_radio_handle_fn,

  /* name */
  "ATMEL_RADIO",

  /* desc */
  "\tThe ATMEL_RADIO app adds support for the atmel radio.\n"
};

#define TRX_REGISTER_BASEADDR 0x140
inline void reg_write(u16 addr, u8 val)
{
  *(u8*)(TRX_REGISTER_BASEADDR + addr) = val;
}

inline u8 reg_read(u16 addr)
{
  return *(u8*)(TRX_REGISTER_BASEADDR + addr);
}
inline void reg_bit_write(u16 addr, u8 pos, u8 value)
{
  u8 old, mask;
  mask = ~(1 << pos);
  old = reg_read(addr) & ~mask; //bits to keep
  old = old | (value << pos); //bit to add
  reg_write(addr, old); //write byte
}


void atmel_radio_set_state(u8 state) //based on zigduino-radio, radio_rfa.c
{
  u8 cmd, retries;
  /* ensure not in state transition */
  while (STATE_TRANSITION_IN_PROGRESS == (STATE_TRANSITION_IN_PROGRESS &TRX_STATE)) {}
  switch(state) {
  case TRX_OFF:
    cmd = CMD_TRX_OFF;
    break;
  case PLL_ON:
    cmd = CMD_PLL_ON;
    break;
  case BUSY_TX:
    cmd = CMD_TX_START;
    break;
  default: //doesn't exist
    cmd = CMD_RX_ON;
    break;
  }

  TRX_STATE = cmd;
  retries = 140; /* enough to receive ongoing frame */
  do {
    if (state == (state & TRX_STATUS)) {
      break;
    }
    retries--;
    _delay_ms(32);
  } while (retries);
}

void atmel_radiosetup(){
  u8 status;
  /* initialize transceiver
     code based on zigduino-radio
  */
  //TRX_RESET_LOW
  TRXPR &= ~(1 << TRXRST);

  //TRX_SLPTR_LOW.  Make sure radio isn't sleeping
  TRXPR  &= ~(1 << SLPTR);

  _delay_ms(6/1000.0);
  //TRX_RESET_HIGH
  TRXPR |= (1 << TRXRST);

  /* disable IRQ and clear any pending IRQs */
  {
    IRQ_MASK = 0;
    /* clear IRQ history by reading status*/
    status = IRQ_STATUS;
  }

  // unset auto crc
  TRX_CTRL_1 &= 0xDF & ~(1 << TX_AUTO_CRC_ON);

  /* enter TRX_OFF state */
  atmel_radio_set_state(TRX_OFF);

  /* enter RX_ON state */
  atmel_radio_set_state(RX_ON);

}


void atmel_radio_pokebyte(u16 addr, u8 data) {
  reg_write(addr, data);
}

u8 atmel_radio_peekbyte(u16 addr) {
  return reg_read(addr);
}

//! Writes bytes into the Atmel's ram
void atmel_radio_pokeram(u16 addr, u8 *data, u16 len){
  u16 i;
  for (i = 0; i < len; i++ ) {
    atmel_radio_pokebyte(addr+i, data[i]);
  }
}

//! Read bytes from the Atmel's RAM.
void atmel_radio_peekram(u16 addr, u8 *data, u16 len){
  u16 i;
  //Data goes here.
  for (i = 0; i < len; i++){
    *data++=atmel_radio_peekbyte(addr+i);
  }
}

int atmel_radio_is_frame_buffer_empty() {
  return TRXFBST == 0;
}

void atmel_radio_clear_frame_buffer() {
  TRXFBST = 0; //reset the frame buffer pointer to signal it was read
}

//! Handles a Chipcon SPI command.
void atmel_radio_handle_fn( uint8_t const app,
                            uint8_t const verb,
                            uint32_t const len){

  u16 length;
  u8  len8;

  switch(verb){
  case PEEK:

  case READ:
    length=cmddataword[1]; // Backup length. Second byte
    atmel_radio_peekram(cmddataword[0], // First word is address
                        cmddata, // Return in same buffer
                        length);
    txdata(app,verb,length);
    break;
  case WRITE:
  case POKE:
    atmel_radio_pokeram(cmddataword[0], // First word is address
                        cmddata+2,  // Remainder of buffer is data
                        len-2); //Length implied by packet length
    txdata(app,verb,len-2); //return number of poked bytes
    break;
  case SETUP:
    atmel_radiosetup();
    txdata(app,verb,0);
    break;

  case ATMEL_RADIO_RX:

    // set to PLL_ON so frame buffer isn't clobbered
    atmel_radio_set_state(PLL_ON);
    len8 = 8;
    if (!atmel_radio_is_frame_buffer_empty()) { //only if we recieved something new
      len8 = TST_RX_LENGTH; //register contains frame length

      if  ((len8 > 0x80) ) { //frame too big
        txdata(app,verb,0);
      } else {
        memcpy(cmddata, (void *) &TRXFBST, len8); //return in same buffer
        atmel_radio_clear_frame_buffer();
        txdata(app, verb, len8);
      }
    }else{
      // didn't recieve anything new
      txdata(app,verb,0);
    }
    // receive packets again
    atmel_radio_set_state(RX_ON);

    break;
  case ATMEL_RADIO_TX:
    //prevent radio from recieving new packets
    atmel_radio_set_state(PLL_ON);
    if (cmddata[0] > 127) { //truncate too long packets
      cmddata[0] = 127;
    }

    memcpy((void *) &TRXFBST, cmddata, cmddata[0]+1); //copy length + packet
    atmel_radio_set_state(BUSY_TX); //send packet

    while (PLL_ON != (PLL_ON & TRX_STATUS)) {} //wait for TX done
    //reset the frame buffer pointer to signal it was read
    atmel_radio_clear_frame_buffer();
    atmel_radio_set_state(RX_ON);
    txdata(app, verb, len8);

    break;

  case ATMEL_RADIO_RX_FLUSH:
  case ATMEL_RADIO_TX_FLUSH:
  default:
    debugstr("Not yet supported in ATMEL_RADIO");
    txdata(app,verb,-1);
    break;
  }

}
