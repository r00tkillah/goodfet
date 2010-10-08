/*! \file jtag.h
  \author Travis Goodspeed
  \brief JTAG handler functions.
*/

#ifndef JTAG_H
#define JTAG_H

#include <signal.h>
#include <io.h>
#include <iomacros.h>


// Generic Commands

//! Shift n bytes.
unsigned long jtagtransn(unsigned long word,
			 unsigned char bitcount,
             unsigned char flags);
//! Shift the address width.
unsigned long jtag_dr_shiftadr(unsigned long in);
//! Shift 8 bits of the IR.
unsigned char jtag_ir_shift8(unsigned char);
//! Shift 16 bits of the DR.
unsigned int jtag_dr_shift16(unsigned int);
//! Shift 20 bits of the DR, MSP430 specific.
unsigned long jtag_dr_shift20(unsigned long in);
//! Stop JTAG, release pins
void jtag_stop();

//! Setup the JTAG pin directions.
void jtagsetup();

//! Ratchet Clock Down and Up
void jtag_tcktock();
//! Go to SHIFT_IR
void jtag_goto_shift_ir();
//! Go to SHIFT_DR
void jtag_goto_shift_dr();
//! TAP RESET
void jtag_resettap();

//Pins.  Both SPI and JTAG names are acceptable.
//#define SS   BIT0
#define MOSI BIT1
#define MISO BIT2
#define SCK  BIT3

#define TMS BIT0
#define TDI BIT1
#define TDO BIT2
#define TCK BIT3

#define TCLK TDI

//These are not on P5
#define RST BIT6
#define TST BIT0

//This could be more accurate.
//Does it ever need to be?
#define JTAGSPEED 20
#define JTAGDELAY(x) delay(x)

#define SETMOSI P5OUT|=MOSI
#define CLRMOSI P5OUT&=~MOSI
#define SETCLK P5OUT|=SCK
#define CLRCLK P5OUT&=~SCK
#define READMISO (P5IN&MISO?1:0)
#define SETTMS P5OUT|=TMS
#define CLRTMS P5OUT&=~TMS
#define SETTCK P5OUT|=TCK
#define CLRTCK P5OUT&=~TCK
#define SETTDI P5OUT|=TDI
#define CLRTDI P5OUT&=~TDI

#define SETTST P4OUT|=TST
#define CLRTST P4OUT&=~TST
#define SETRST P2OUT|=RST
#define CLRRST P2OUT&=~RST

#define SETTCLK SETTDI
#define CLRTCLK CLRTDI

extern int savedtclk;
#define SAVETCLK savedtclk=P5OUT&TCLK;
#define RESTORETCLK if(savedtclk) P5OUT|=TCLK; else P5OUT&=~TCLK

//Replace every "CLRTCK SETTCK" with this.
#define TCKTOCK CLRTCK,SETTCK

//JTAG commands
#define JTAG_IR_SHIFT 0x80
#define JTAG_DR_SHIFT 0x81
#define JTAG_RESETTAP 0x82
#define JTAG_RESETTARGET 0x83
#define JTAG_DR_SHIFT20 0x91

#define MSB         0
#define LSB         1
#define NOEND       2
#define NORETIDLE   4


//JTAG430 commands
//#include "jtag430.h"
#define Exit2_DR 0x0
#define Exit_DR 0x1
#define Shift_DR 0x2
#define Pause_DR 0x3
#define Select_IR 0x4
#define Update_DR 0x5
#define Capture_DR 0x6
#define Select_DR 0x7
#define Exit2_IR 0x8
#define Exit_IR 0x9
#define Shift_IR 0xa
#define Pause_IR 0xb
#define RunTest_Idle 0xc
#define Update_IR 0xd
#define Capture_IR 0xe
#define Test_Reset 0xf
                                                                                                                                
#endif
