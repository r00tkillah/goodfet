/*! \file ccspi.c
  \author Travis Goodspeed
  \brief Chipcon SPI Register Interface

  Unfortunately, there is very little similarity between the CC2420
  and the CC2500, to name just two of the myriad of Chipcon SPI
  radios.  Auto-detection will be a bit difficult, but more to the
  point, all high level functionality must be moved into the client.
*/

//Higher level left to client application.

#include "platform.h"
#include "command.h"
#include <stdlib.h> //added for itoa

#include "ccspi.h"
#include "spi.h"

//! Handles a Chipcon SPI command.
void ccspi_handle_fn( uint8_t const app,
		      uint8_t const verb,
		      uint32_t const len);

// define the ccspi app's app_t
app_t const ccspi_app = {

	/* app number */
	CCSPI,

	/* handle fn */
	ccspi_handle_fn,

	/* name */
	"CCSPI",

	/* desc */
	"\tThe CCSPI app adds support for the Chipcon SPI register\n"
	"\tinterface. Unfortunately, there is very little similarity\n"
	"\tbetween the CC2420 and the CC2500, to name just two of the\n"
	"\tmyriad of Chipcon SPI radios.  Auto-detection will be a bit\n"
	"\tdifficult, but more to the point, all high level functionality\n"
	"\tmust be moved into the client.\n"
};

//! Set up the pins for CCSPI mode.
void ccspisetup(){
  SPIDIR&=~MISO;
  SPIDIR|=MOSI+SCK;
  DIRSS;
  DIRCE;

  P4OUT|=BIT5; //activate CC2420 voltage regulator
  msdelay(100);

  //Reset the CC2420.
  P4OUT&=~BIT6;
  P4OUT|=BIT6;

  //Begin a new transaction.
  CLRSS;
  SETSS;
}

//! Read and write an CCSPI byte.
u8 ccspitrans8(u8 byte){
  register unsigned int bit;
  //This function came from the CCSPI Wikipedia article.
  //Minor alterations.

  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      SETMOSI;
    else
      CLRMOSI;
    byte <<= 1;

    SETCLK;

    /* read MISO on trailing edge */
    byte |= READMISO;
    CLRCLK;
  }

  return byte;
}


//! Reflexively jam on the present channel.
void ccspireflexjam(u16 delay){
  unsigned long i;
  #if defined(FIFOP) && defined(SFD) && defined(FIFO) && defined(PLED2DIR) && defined(PLED2PIN) && defined(PLED2OUT)
  
  prep_timer();
  debugstr("Reflex jamming until reset.");
  debughex(delay);
  txdata(CCSPI,CCSPI_REFLEX,1);  //Let the client continue its business.
  while(1) {
    //Wait until a packet is received
    while(!SFD){
      //Has there been an overflow in the RX buffer?
      if((!FIFO)&&FIFOP){
	//debugstr("Clearing RX overflow");
	CLRSS;
	ccspitrans8(0x08); //SFLUSHRX
	SETSS;
      }
    }
    //Turn on LED 2 (green) as signal
    PLED2DIR |= PLED2PIN;
    PLED2OUT &= ~PLED2PIN;
    
    
    
    //Wait a few us to send it.
    delay_us(delay);

    //Transmit the packet.
    CLRSS;
    ccspitrans8(0x04);
    SETSS;
    
    
    //Load the next jamming packet.
    //Note: attempts to preload this actually slowed the jam time down from 7 to 9 bytes.
    CLRSS;
    ccspitrans8(CCSPI_TXFIFO);
    char pkt[5] = {0x05, 0, 0, 0, 0};
    //char pkt[15] = {0x0f, 0x01, 0x08, 0x82, 0xff, 0xff, 0xff, 0xff, 0xde, 0xad, 0xbe, 0xef, 0xba, 0xbe, 0xc0};
    //char pkt[12] = {0x0c, 0x01, 0x08, 0x82, 0xff, 0xff, 0xff, 0xff, 0xde, 0xad, 0xbe, 0xef};
    for(i=0;i<pkt[0];i++)
      ccspitrans8(pkt[i]);
    SETSS;
    
    //* I think this might be unnecessary.
    //msdelay(100+delay);      //Instead of waiting for pulse on SFD
    //delay_ms(1);
    //Flush TX buffer.
    CLRSS;
    ccspitrans8(0x09); //SFLUSHTX
    SETSS;
    
    
    //Turn off LED 2 (green) as signal
    PLED2DIR |= PLED2PIN;
    PLED2OUT |= PLED2PIN;
  }
#else
  debugstr("Can't reflexively jam without SFD, FIFO, FIFOP, and P2LEDx definitions - try using telosb platform.");
  txdata(CCSPI,NOK,0);
#endif
}



//! Writes a register
u8 ccspi_regwrite(u8 reg, const u8 *buf, int len){
  CLRSS;

  reg=ccspitrans8(reg);
  while(len--)
    ccspitrans8(*buf++);

  SETSS;
  return reg;//status
}
//! Reads a register
u8 ccspi_regread(u8 reg, u8 *buf, int len){
  CLRSS;

  reg=ccspitrans8(reg);
  while(len--)
    *buf++=ccspitrans8(0);

  SETSS;
  return reg;//status
}

//! Handles a Chipcon SPI command.
void ccspi_handle_fn( uint8_t const app,
		      uint8_t const verb,
		      uint32_t const len){
  unsigned long i;
  u8 j;

  //debugstr("Chipcon SPI handler.");

  switch(verb){
  case PEEK:
    cmddata[0]|=0x40; //Set the read bit.
    //DO NOT BREAK HERE.
  case READ:
  case WRITE:
  case POKE:
    CLRSS; //Drop !SS to begin transaction.
    j=cmddata[0];//Backup address.
    for(i=0;i<len;i++)
      cmddata[i]=ccspitrans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    cmddata[0]=j&~0x40;//Restore address.
    txdata(app,verb,len);
    break;
  case SETUP:
    ccspisetup();
    txdata(app,verb,0);
    break;
  case CCSPI_RX:
#ifdef FIFOP
    //Has there been an overflow?
    if((!FIFO)&&FIFOP){
      //debugstr("Clearing overflow");
      CLRSS;
      ccspitrans8(0x08); //SFLUSHRX
      SETSS;
    }

    //Is there a packet?
    if(FIFOP&&FIFO){
      //Wait for completion.
      while(SFD);
      
      //Get the packet.
      CLRSS;
      ccspitrans8(CCSPI_RXFIFO | 0x40);
      //ccspitrans8(0x3F|0x40);
      cmddata[0]=0xff; //to be replaced with length
      for(i=0;i<cmddata[0]+2;i++)
        cmddata[i]=ccspitrans8(0xde);
      SETSS;

      //Flush buffer.
      CLRSS;
      ccspitrans8(0x08); //SFLUSHRX
      SETSS;
      
      
      //Only should transmit length of one more than the reported
      // length of the frame, which holds the length byte:
      txdata(app,verb,cmddata[0]+1);
    }else{
      //No packet.
      txdata(app,verb,0);
    }
#else
    debugstr("Can't RX a packet with SFD and FIFOP definitions.");
    txdata(app,NOK,0);
#endif
    break;
  case CCSPI_RX_FLUSH:
    //Flush the buffer.
    CLRSS;
    ccspitrans8(CCSPI_SFLUSHRX);
    SETSS;

    txdata(app,verb,0);
    break;

  case CCSPI_REFLEX:
    ccspireflexjam(len?cmddataword[0]:0);
    break;

  case CCSPI_REFLEX_AUTOACK:
#if defined(FIFOP) && defined(SFD) && defined(FIFO) && defined(PLED2DIR) && defined(PLED2PIN) && defined(PLED2OUT)
    //txdata(app, verb, 1);
    debugstr("AutoACK");
    char byte[4];
    while(1) {
        //Has there been an overflow in the RX buffer?
        if((!FIFO)&&FIFOP){
          //debugstr("Clearing overflow");
          CLRSS;
          ccspitrans8(0x08); //SFLUSHRX
          SETSS;
        }

        //Wait until a packet is received
        while(!SFD);
        //Turn on LED 2 (green) as signal
	    PLED2DIR |= PLED2PIN;
	    PLED2OUT &= ~PLED2PIN;

        //Put radio in TX mode
        //Note: Not doing this slows down jamming, so can't jam short packets.
        //      However, if we do this, it seems to mess up our RXFIFO ability.
        //CLRSS;
        //ccspitrans8(0x04);
        //SETSS;
        //Load the jamming packet
        CLRSS;
        ccspitrans8(CCSPI_TXFIFO);
        char pkt[7] = {0x07, 0x01, 0x08, 0xff, 0xff, 0xff, 0xff};
        for(i=0;i<pkt[0];i++)
          ccspitrans8(pkt[i]);
        SETSS;
        //Transmit the jamming packet
        CLRSS;
        ccspitrans8(0x04);  //STXON
        SETSS;
        msdelay(200);       //Instead of examining SFD line status
        //Flush TX buffer.
        CLRSS;
        ccspitrans8(0x09);  //SFLUSHTX
        SETSS;

        //Get the orignally received packet, up to the seqnum field.
        CLRSS;
        ccspitrans8(CCSPI_RXFIFO | 0x40);
        for(i=0;i<4;i++)
            cmddata[i]=ccspitrans8(0xde);
        SETSS;
        //Flush RX buffer.
        CLRSS;
        ccspitrans8(0x08); //SFLUSHRX
        SETSS;
        //Send the sequence number of the jammed packet back to the client
        //itoa(cmddata[3], byte, 16);
        //debugstr(byte);
        //txdata(app,verb,cmddata[3]);

        //TODO turn on AUTOCRC for it to apply to the TX???
        //     this may overcome issues of bad crc / length issues?
        //mdmctrl0 (0x11) register set bit 5 to true.

        //Create the forged ACK packet
        cmddata[0] = 6;     //length of ack frame plus length
        cmddata[1] = 0x02;  //first byte of FCF
        cmddata[2] = 0x00;  //second byte of FCF
        //[3] is already filled with the sequence number
        int crc = 0;
        for(i=1;i<4;i++) {
            int c = cmddata[i];
            int q = (crc ^ c) & 15;   		//Do low-order 4 bits
            crc = (crc / 16) ^ (q * 4225);
            q = (crc ^ (c / 16)) & 15;		//And high 4 bits
            crc = (crc / 16) ^ (q * 4225);
        }
        cmddata[4] = crc & 0xFF;
        cmddata[5] = (crc >> 8) & 0xFF;

        for(i=0;i<cmddata[0];i++) {
            itoa(cmddata[i], byte, 16);
            debugstr(byte);
        }
        //Load the forged ACK packet
        CLRSS;
        ccspitrans8(CCSPI_TXFIFO);
        for(i=0;i<cmddata[0];i++)
          ccspitrans8(cmddata[i]);
        SETSS;
        //Transmit the forged ACK packet
        while(SFD);
        CLRSS;
        ccspitrans8(0x04);  //STXON
        SETSS;
        msdelay(200);       //TODO try doing this based on SFD line status instead
        //Flush TX buffer
        CLRSS;
        ccspitrans8(0x09);  //SFLUSHTX
        SETSS;

        //TODO disable AUTOCRC here again to go back to promiscous mode

        //Turn off LED 2 (green) as signal
	    PLED2DIR |= PLED2PIN;
	    PLED2OUT |= PLED2PIN;
    }
    //TODO the firmware stops staying in this mode after a while, and stops jamming... need to find a fix.
#else
    debugstr("Can't reflexively jam without SFD, FIFO, FIFOP, and P2LEDx definitions - try using telosb platform.");
    txdata(app,NOK,0);
#endif
    break;

  case CCSPI_TX_FLUSH:
    //Flush the buffer.
    CLRSS;
    ccspitrans8(CCSPI_SFLUSHTX);
    SETSS;

    txdata(app,verb,0);
    break;
  case CCSPI_TX:
#ifdef FIFOP

    //Wait for last packet to TX.
    //while(ccspi_status()&BIT3);
    
    //Flush TX buffer.
    CLRSS;
    ccspitrans8(0x09); //SFLUSHTX
    SETSS;
    

    //Load the packet.
    CLRSS;
    ccspitrans8(CCSPI_TXFIFO);
    for(i=0;i<cmddata[0];i++)
      ccspitrans8(cmddata[i]);
    SETSS;

    //Transmit the packet.
    CLRSS;
    ccspitrans8(0x04); //STXON
    SETSS;

    //Wait for the pulse on SFD, after which the packet has been sent.
    while(!SFD);
    while(SFD);
    
    txdata(app,verb,0);
#else
    debugstr("Can't TX a packet with SFD and FIFOP definitions.");
    txdata(app,NOK,0);
#endif
    break;
  default:
    debugstr("Not yet supported in CCSPI");
    txdata(app,verb,0);
    break;
  }

}
