/*! \file jtagarm7tdmi.h
  \brief JTAG handler functions for the ARM7TDMI family of processors
*/

#include "jtag.h"


#define JTAGSTATE_ARM 0         // bit 4 on dbg status reg is low
#define JTAGSTATE_THUMB 1

#define ARMTCKTOCK  CLRTCK; PLEDOUT^=PLEDPIN; SETTCK; PLEDOUT^=PLEDPIN;
// ASSUME RUN-TEST/IDLE STATE
#define SHIFT_IR    SETTMS;TCKTOCK;TCKTOCK;CLRTMS;TCKTOCK;TCKTOCK;
#define SHIFT_DR    SETTMS;TCKTOCK;CLRTMS;TCKTOCK;TCKTOCK;



unsigned char current_chain;
unsigned char current_dbgstate = -1;
unsigned char last_halt_debug_state = -1;
unsigned long last_halt_pc = -1;
unsigned long count_dbgspd_instr_since_debug = 0;
unsigned long count_sysspd_instr_since_debug = 0;


void jtag_goto_shift_ir();
void jtag_goto_shift_dr();
void jtag_reset_to_runtest_idle();
void jtag_arm_tcktock();


// JTAGARM7TDMI Commands

//! Write data to address.
unsigned long jtagarm7tdmi_writemem(unsigned long adr, unsigned long data);
//! Read data from address
unsigned long jtagarm7tdmi_readmem(unsigned long adr);

//! Halt the CPU
unsigned long jtagarm7tdmi_haltcpu();
//! Release the CPU
unsigned long jtagarm7tdmi_releasecpu();

//! Set the program counter.
void jtagarm7tdmi_setpc(unsigned long adr);

//! Write data to address.
unsigned long jtagarm7tdmi_writeflash(unsigned long adr, unsigned long data);


//! Start JTAG
unsigned long jtagarm7tdmi_start(void);
//! Reset TAP State Machine
void jtagarm7tdmi_resettap();

//! ARM-specific JTAG bit-transfer
unsigned long jtagarmtransn(unsigned long word, unsigned char bitcount, unsigned char lsb, unsigned char end, unsigned char retidle);

//! Grab debug register - Expect chain 2 to be selected
unsigned long jtagarm7tdmi_get_dbgstate() ;
//! Grab the core ID.
unsigned long jtagarm7tdmi_idcode();
//!  Connect Bypass Register to TDO/TDI
unsigned char jtagarm7tdmi_bypass();
//!  Connect the appropriate scan chain to TDO/TDI
unsigned long jtagarm7tdmi_scan_intest(int n);
//!  Set a 32-bit ARM register
void jtagarm7tdmi_set_register(unsigned long reg, unsigned long val);
//!  Get a 32-bit ARM register
unsigned long jtagarm7tdmi_get_register(unsigned long reg);

// ARM7TDMI-specific pins
// DBGRQ - GoodFET Pin 8
#define DBGRQ   TST

/*      ARM7TDMI data
The instruction register is 4 bits in length.
There is no parity bit.
The fixed value 0001 is loaded into the instruction register during the CAPTURE-IR
controller state.
The least significant bit of the instruction register is scanned in and scanned out first.
*/

//4-bit ARM7TDMI JTAG commands, bit-swapped
#define ARM7TDMI_IR_EXTEST              0x0
#define ARM7TDMI_IR_SCAN_N              0x2
#define ARM7TDMI_IR_SAMPLE              0x3
#define ARM7TDMI_IR_RESTART             0x4
#define ARM7TDMI_IR_CLAMP               0x5
#define ARM7TDMI_IR_HIGHZ               0x7
#define ARM7TDMI_IR_CLAMPZ              0x9
#define ARM7TDMI_IR_INTEST              0xC
#define ARM7TDMI_IR_IDCODE              0xE
#define ARM7TDMI_IR_BYPASS              0xF

// read 3 bit - Debug Control
#define EICE_DBGCTRL                    0       
#define EICE_DBGCTRL_BITLEN             3
// read 5 bit - Debug Status
#define EICE_DBGSTATUS                  1
#define EICE_DBGSTATUS_BITLEN           5
// read 6 bit - Debug Comms Control Register
#define EICE_DBGCCR                     4
#define EICE_DBGCCR_BITLEN              6
// r/w 32 bit - Debug Comms Data Register
#define EICE_DBGCDR                     5
// r/w 32 bit - Watchpoint 0 Address
#define EICE_WP0ADDR                    8
// r/w 32 bit - Watchpoint 0 Addres Mask
#define EICE_WP0ADDRMASK                9
// r/w 32 bit - Watchpoint 0 Data
#define EICE_WP0DATA                    10
// r/w 32 bit - Watchpoint 0 Data Masl
#define EICE_WP0DATAMASK                11
// r/w 9 bit - Watchpoint 0 Control Value
#define EICE_WP0CTRL                    12
// r/w 8 bit - Watchpoint 0 Control Mask
#define EICE_WP0CTRLMASK                13
// r/w 32 bit - Watchpoint 0 Address
#define EICE_WP1ADDR                    16
// r/w 32 bit - Watchpoint 0 Addres Mask
#define EICE_WP1ADDRMASK                17
// r/w 32 bit - Watchpoint 0 Data
#define EICE_WP1DATA                    18
// r/w 32 bit - Watchpoint 0 Data Masl
#define EICE_WP1DATAMASK                19
// r/w 9 bit - Watchpoint 0 Control Value
#define EICE_WP1CTRL                    20
// r/w 8 bit - Watchpoint 0 Control Mask
#define EICE_WP1CTRLMASK                21


#define NOEND 0
#define END 1
#define MSB 0
#define LSB 1
#define NORETIDLE 0
#define RETIDLE 1


//JTAGARM7TDMI commands
#define JTAGARM7TDMI_GET_DEBUG_CTRL       0x80
#define JTAGARM7TDMI_SET_DEBUG_CTRL       0x81
#define JTAGARM7TDMI_GET_PC               0x82
#define JTAGARM7TDMI_SET_PC               0x83
#define JTAGARM7TDMI_GET_CHIP_ID          0x84
#define JTAGARM7TDMI_GET_DEBUG_STATE      0x85
#define JTAGARM7TDMI_GET_WATCHPOINT       0x86
#define JTAGARM7TDMI_SET_WATCHPOINT       0x87
#define JTAGARM7TDMI_GET_REGISTER         0x88
#define JTAGARM7TDMI_SET_REGISTER         0x89
#define JTAGARM7TDMI_GET_REGISTERS        0x8a
#define JTAGARM7TDMI_SET_REGISTERS        0x8b
#define JTAGARM7TDMI_HALTCPU              0x8c
#define JTAGARM7TDMI_RELEASECPU           0x8d
#define JTAGARM7TDMI_DEBUG_INSTR          0x8e
#define JTAGARM7TDMI_STEP_INSTR           0x8f
#define JTAGARM7TDMI_WRITEMEM             0x90
#define JTAGARM7TDMI_READMEM              0x91
#define JTAGARM7TDMI_WRITE_FLASH_PAGE     0x92
#define JTAGARM7TDMI_READ_FLASH_PAGE      0x93
#define JTAGARM7TDMI_MASS_ERASE_FLASH     0x94
#define JTAGARM7TDMI_PROGRAM_FLASH        0x95
#define JTAGARM7TDMI_LOCKCHIP             0x96
#define JTAGARM7TDMI_CHIP_ERASE           0x97
// Really ARM specific stuff
#define JTAGARM7TDMI_GET_CPSR             0x98
#define JTAGARM7TDMI_SET_CPSR             0x99
#define JTAGARM7TDMI_GET_SPSR             0x9a
#define JTAGARM7TDMI_SET_SPSR             0x9b
#define JTAGARM7TDMI_SET_MODE_THUMB       0x9c
#define JTAGARM7TDMI_SET_MODE_ARM         0x9d
#define JTAGARM7TDMI_SET_IR               0x9e
#define JTAGARM7TDMI_WAIT_DBG             0x9f
#define JTAGARM7TDMI_SHIFT_DR             0xa0
#define JTAGARM7TDMI_SETWATCH0            0xa1
#define JTAGARM7TDMI_SETWATCH1            0xa2
#define JTAGARM7TDMI_CHAIN0               0xa3


// for deeper understanding, read the instruction cycle timing section of: 
//      http://www.atmel.com/dyn/resources/prod_documents/DDI0029G_7TDMI_R3_trm.pdf
#define EXECNOPARM                  0xe1a00000L
#define ARM_INSTR_NOP               0xe1a00000L
#define ARM_INSTR_BX_R0             0xe12fff10L
#define ARM_INSTR_STR_Rx_r14        0xe58f0000L // from atmel docs
#define ARM_READ_REG                ARM_INSTR_STR_Rx_r14
#define ARM_INSTR_LDR_Rx_r14        0xe59f0000L // from atmel docs
#define ARM_WRITE_REG               ARM_INSTR_LDR_Rx_r14
#define ARM_INSTR_LDR_R1_r0_4       0xe4901004L
#define ARM_READ_MEM                ARM_INSTR_LDR_R1_r0_4
#define ARM_INSTR_STR_R1_r0_4       0xe4801004L
#define ARM_WRITE_MEM               ARM_INSTR_STR_R1_r0_4
#define ARM_INSTR_MRS_R0_CPSR       0xe10f0000L
#define ARM_INSTR_MSR_cpsr_cxsf_R0  0xe12ff000L
#define ARM_INSTR_STMIA_R14_r0_rx   0xE88E0000L      // add up to 65k to indicate which registers...
#define ARM_STORE_MULTIPLE          ARM_INSTR_STMIA_R14_r0_rx
#define ARM_INSTR_SKANKREGS         0xE88F7fffL
#define ARM_INSTR_CLOBBEREGS        0xE89F7fffL

#define ARM_INSTR_B_IMM             0xea000000L
#define ARM_INSTR_BX_PC             0xe12fff10L      // need to set r0 to the desired address
#define THUMB_INSTR_STR_R0_r0       0x60006000L
#define THUMB_INSTR_MOV_R0_PC       0x46b846b8L
#define THUMB_INSTR_BX_PC           0x47784778L
#define THUMB_INSTR_NOP             0x1c001c00L
#define ARM_REG_PC                  15

#define JTAG_ARM7TDMI_DBG_DBGACK    1
#define JTAG_ARM7TDMI_DBG_DBGRQ     2
#define JTAG_ARM7TDMI_DBG_IFEN      4
#define JTAG_ARM7TDMI_DBG_cgenL     8
#define JTAG_ARM7TDMI_DBG_TBIT      16

