/*! 
  \file jtagxscale.h
  \author Dave Huseby <huseby at linuxprogrammer.org>
  \brief Intel XScale JTAG
*/

/* NOTE: I heavily cribbed from the ARM7TDMI jtag implementation. Credit where
 * credit is due. */

#ifndef JTAGXSCALE_H
#define JTAGXSCALE_H

#include "app.h"

#define JTAGXSCALE 0x15

/* 
 * Utility Macros 
 */

/* XTT (LED TCK TOCK) toggles the CLK line while turning on/off the LED */
#define XTT             CLRTCK;PLEDOUT^=PLEDPIN;SETTCK;PLEDOUT^=PLEDPIN;

/* RUN_TEST_IDLE gets us into run-test-idle from anywhere in the TAP FSM */
#define RUN_TEST_IDLE   SETTMS;XTT;XTT;XTT;XTT;XTT;XTT;XTT;XTT;CLRTMS;XTT;

/* SHIFT_IR gets us into the "Shift IR" state from the run-test-idle state */
#define SHIFT_IR        SETTMS;XTT;XTT;CLRTMS;XTT;XTT;

/* SHIFT_DIR gets us into the "Shift DR" state from the run-test-idle state */
#define SHIFT_DR        SETTMS;XTT;CLRTMS;XTT;XTT;


/*
 * XScale 5-bit JTAG Commands
 */

/* On the XScale chip, the TDI pin is connected to the MSB of the IR and the 
 * TDO is connected to the LSB.  That means we have to shift these commands 
 * in from LSB to MSB order. */

/* 01000 - High Z
 * The highz instruction floats all three-stateable output and in/out pins. 
 * Also, when this instruction is active, the Bypass register is connected 
 * between TDI and TDO. This register can be accessed via the JTAG Test-Access 
 * Port throughout the device operation. Access to the Bypass register can also 
 * be obtained with the bypass instruction. */
#define XSCALE_IR_HIGHZ             0x08

/* 11110 - Get ID Code
 * The idcode instruction is used in conjunction with the device identification 
 * register. It connects the identification register between TDI and TDO in the 
 * Shift_DR state. When selected, idcode parallel-loads the hard-wired 
 * identification code (32 bits) on TDO into the identification register on the 
 * rising edge of TCK in the Capture_DR state. Note: The device identification 
 * register is not altered by data being shifted in on TDI.*/
#define XSCALE_IR_IDCODE            0x1E

/* 11111 - Bypass
 * The bypass instruction selects the Bypass register between TDI and TDO pins 
 * while in SHIFT_DR state, effectively bypassing the processor’s test logic. 
 * 02 is captured in the CAPTURE_DR state. While this instruction is in effect, 
 * all other test data registers have no effect on the operation of the system. 
 * Test data registers with both test and system functionality perform their 
 * system functions when this instruction is selected. */
#define XSCALE_IR_BYPASS            0x1F

/*
 * GoodFET Commands from the Client
 */

/* Get CHIP ID */
#define XSCALE_GET_CHIP_ID          0xF1


/*
 * Public Interface
 */

/* this handles shifting arbitrary length bit strings into the instruction
 * register and clocking out bits while leaving the JTAG state machine in a
 * known state. it also handle bit swapping. */
unsigned long jtag_xscale_shift_n(unsigned long word,
                                  unsigned char nbits,
                                  unsigned char flags);

/* this handles shifting in the IDCODE instruction and shifting the result
 * out the TDO and return it. */
unsigned long jtag_xscale_idcode();

extern app_t const jtagxscale_app;

#endif // JTAGXSCALE_H

