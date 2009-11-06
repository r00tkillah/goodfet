/*! \file chipcon.c
  \author Travis Goodspeed
  \brief Chipcon 8051 debugging.
*/


//This is like SPI, except that you read or write, not both.

/* N.B. The READ verb performs a write of all (any) supplied data,
   then reads a single byte reply from the target.  The WRITE verb
   only writes.
*/

#include "platform.h"
#include "command.h"
#include "chipcon.h"

#include <signal.h>
#include <io.h>
#include <iomacros.h>


/* Concerning clock rates, the maximimum clock rates are defined on
   page 4 of the spec.  They vary, but are roughly 30MHz.  Raising
   this clock rate might allow for clock glitching, but the GoodFET
   isn't sufficient fast for that.  Perhaps a 200MHz ARM or an FPGA in
   the BadassFET?
*/

//Pins and I/O
//MISO and MOSI are the same pin, direction changes.
#define RST  BIT0
#define MOSI BIT2
#define MISO BIT2
#define SCK  BIT3

//This could be more accurate.
//Does it ever need to be?
#define CCSPEED 3
#define CCDELAY(x) delay(x)

#define SETMOSI P5OUT|=MOSI
#define CLRMOSI P5OUT&=~MOSI
#define SETCLK P5OUT|=SCK
#define CLRCLK P5OUT&=~SCK
#define READMISO (P5IN&MISO?1:0)

#define CCWRITE P5DIR|=MOSI
#define CCREAD P5DIR&=~MISO

//! Set up the pins for CC mode.  Does not init debugger.
void ccsetup(){
  P5OUT|=MOSI+SCK+RST;
  P5DIR|=MOSI+SCK+RST;
  //P5DIR&=~MISO;  //MOSI is MISO
}

//! Initialize the debugger
void ccdebuginit(){
  //Two positive debug clock pulses while !RST is low.
  //Take RST low, pulse twice, then high.
  P5OUT&=~SCK;
  P5OUT&=~RST;
  
  //pulse twice
  CCDELAY(CCSPEED);
  P5OUT|=SCK;  //up
  CCDELAY(CCSPEED);
  P5OUT&=~SCK; //down
  CCDELAY(CCSPEED);
  P5OUT|=SCK;  //up
  CCDELAY(CCSPEED);
  P5OUT&=~SCK; //down
  
  //Raise !RST.
  P5OUT|=RST;
}

//! Read and write a CC bit.
unsigned char cctrans8(unsigned char byte){
  unsigned int bit;
  //This function came from the SPI Wikipedia article.
  //Minor alterations.
  
  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      SETMOSI;
    else
      CLRMOSI;
    byte <<= 1;
 
    /* half a clock cycle before leading/rising edge */
    CCDELAY(CCSPEED/2);
    SETCLK;
 
    /* half a clock cycle before trailing/falling edge */
    CCDELAY(CCSPEED/2);
 
    /* read MISO on trailing edge */
    byte |= READMISO;
    CLRCLK;
  }
  
  return byte;
}

//! Send a command from txbytes.
void cccmd(unsigned char len){
  unsigned char i;
  CCWRITE;
  for(i=0;i<len;i++)
    cctrans8(cmddata[i]);
}

//! Fetch a reply, usually 1 byte.
void ccread(unsigned char len){
  unsigned char i;
  CCREAD;
  for(i=0;i<len;i++)
    cmddata[i]=cctrans8(0);
}

//! Handles a monitor command.
void cchandle(unsigned char app,
	       unsigned char verb,
	       unsigned long len){
  //Always init.  Might help with buggy lines.
  //Might hurt too.
  //ccdebuginit();
  long i;
  
  switch(verb){
    //CC_PEEK and CC_POKE will come later.
  case PEEK:
    cmddata[0]=cc_peekirambyte(cmddata[0]);
    txdata(app,verb,1);
    break;
  case POKE:
    cmddata[0]=cc_pokeirambyte(cmddata[0],cmddata[1]);
    txdata(app,verb,0);
    break;
  case READ:  //Write a command and return 1-byte reply.
    cccmd(len);
    ccread(1);
    txdata(app,verb,1);
    break;
  case WRITE: //Write a command with no reply.
    cccmd(len);
    txdata(app,verb,0);
    break;
  case START://enter debugger
    ccdebuginit();
    txdata(app,verb,0);
    break;
  case STOP://exit debugger
    //Take RST low, then high.
    P5OUT&=~RST;
    CCDELAY(CCSPEED);
    P5OUT|=RST;
    txdata(app,verb,0);
    break;
  case SETUP:
    ccsetup();
    txdata(app,verb,0);
    break;
    
  //Micro commands!
  case CC_CHIP_ERASE:
    cc_chip_erase();
    txdata(app,verb,1);
    break;
  case CC_WR_CONFIG:
    cc_wr_config(cmddata[0]);
    txdata(app,verb,1);
    break;
  case CC_RD_CONFIG:
    cc_rd_config();
    txdata(app,verb,1);
    break;
  case CC_GET_PC:
    cc_get_pc();
    txdata(app,verb,2);
    break;
  case CC_LOCKCHIP:
    cc_lockchip();
    //no break, return status
  case CC_READ_STATUS:
    cc_read_status();
    txdata(app,verb,1);
    break;
  case CC_SET_HW_BRKPNT:
    cc_set_hw_brkpnt(cmddataword[0]);
    txdata(app,verb,1);
    break;
  case CC_HALT:
    cc_halt();
    txdata(app,verb,1);
    break;
  case CC_RESUME:
    cc_resume();
    txdata(app,verb,1);
    break;
  case CC_DEBUG_INSTR:
    cc_debug_instr(len);
    txdata(app,verb,1);
    break;
  case CC_STEP_INSTR:
    cc_step_instr();
    txdata(app,verb,1);
    break;
  case CC_STEP_REPLACE:
    txdata(app,NOK,0);//TODO add me
    break;
  case CC_GET_CHIP_ID:
    cc_get_chip_id();
    txdata(app,verb,2);
    break;


  //Macro commands
  case CC_READ_CODE_MEMORY:
    cmddata[0]=cc_peekcodebyte(cmddataword[0]);
    txdata(app,verb,1);
    break;
  case CC_READ_XDATA_MEMORY:
    cmddata[0]=cc_peekdatabyte(cmddataword[0]);
    txdata(app,verb,1);
    break;
  case CC_WRITE_XDATA_MEMORY:
    cmddata[0]=cc_pokedatabyte(cmddataword[0], cmddata[2]);
    txdata(app,verb,1);
    break;
  case CC_SET_PC:
    cc_set_pc(cmddatalong[0]);
    txdata(app,verb,0);
    break;
  case CC_WRITE_FLASH_PAGE:
    cc_write_flash_page(cmddatalong[0]);
    txdata(app,verb,0);
    break;
  case CC_WIPEFLASHBUFFER:
    for(i=0xf000;i<0xf800;i++)
      cc_pokedatabyte(i,0xFF);
    txdata(app,verb,0);
    break;
  case CC_MASS_ERASE_FLASH:
  case CC_CLOCK_INIT:
  case CC_PROGRAM_FLASH:
    debugstr("This Chipcon command is not yet implemented.");
    txdata(app,NOK,0);//TODO implement me.
    break;
  }
}

//! Set the Chipcon's Program Counter
void cc_set_pc(u32 adr){
  cmddata[0]=0x02;             //SetPC
  cmddata[1]=((adr>>8)&0xff);  //HIBYTE
  cmddata[2]=adr&0xff;         //LOBYTE
  cc_debug_instr(3);
  return;
}

//! Erase all of a Chipcon's memory.
void cc_chip_erase(){
  cmddata[0]=CCCMD_CHIP_ERASE; //0x14
  cccmd(1);
  ccread(1);
}
//! Write the configuration byte.
void cc_wr_config(unsigned char config){
  cmddata[0]=CCCMD_WR_CONFIG; //0x1D
  cmddata[1]=config;
  cccmd(2);
  ccread(1);
}

//! Locks the chip.
void cc_lockchip(){
  register i;
  
  debugstr("Locking chip.");
  cc_wr_config(1);//Select Info Flash 
  if(!(cc_rd_config()&1))
    debugstr("Config forgotten!");
  
  //Clear config page.
  for(i=0;i<2048;i++)
    cc_pokedatabyte(0xf000+i,0);
  cc_write_flash_page(0);
  if(cc_peekcodebyte(0))
    debugstr("Failed to clear info flash byte.");
  
  cc_wr_config(0);  
  if(cc_rd_config()&1)
    debugstr("Stuck in info flash mode!");
}

//! Read the configuration byte.
unsigned char cc_rd_config(){
  cmddata[0]=CCCMD_RD_CONFIG; //0x24
  cccmd(1);
  ccread(1);
  return cmddata[0];
}


//! Read the status register
unsigned char cc_read_status(){
  cmddata[0]=CCCMD_READ_STATUS; //0x3f
  cccmd(1);
  ccread(1);
  return cmddata[0];
}

//! Read the CHIP ID bytes.
unsigned short cc_get_chip_id(){
  unsigned short toret;
  cmddata[0]=CCCMD_GET_CHIP_ID; //0x68
  cccmd(1);
  ccread(2);
  
  //Return the word.
  toret=cmddata[1];
  toret=(toret<<8)+cmddata[1];
  return toret;
}

//! Populates flash buffer in xdata.
void cc_write_flash_buffer(u8 *data, u16 len){
  cc_write_xdata(0xf000, data, len);
}
//! Populates flash buffer in xdata.
void cc_write_xdata(u16 adr, u8 *data, u16 len){
  u16 i;
  for(i=0; i<len; i++){
    cc_pokedatabyte(adr+i,
		    data[i]);
  }
}


//32-bit words, 2KB pages
#define HIBYTE_WORDS_PER_FLASH_PAGE 0x02
#define LOBYTE_WORDS_PER_FLASH_PAGE 0x00
#define FLASHPAGE_SIZE 0x800

//32 bit words
#define FLASH_WORD_SIZE 0x4

const u8 flash_routine[] = {
  //MOV FADDRH, #imm; 
  0x75, 0xAD,
  0x00,//#imm=((address >> 8) / FLASH_WORD_SIZE) & 0x7E,
  
  0x75, 0xAC, 0x00,                                          //                 MOV FADDRL, #00; 
  /* Erase page. */
  0x75, 0xAE, 0x01,                                          //                 MOV FLC, #01H; // ERASE 
                                                             //                 ; Wait for flash erase to complete 
  0xE5, 0xAE,                                                // eraseWaitLoop:  MOV A, FLC; 
  0x20, 0xE7, 0xFB,                                          //                 JB ACC_BUSY, eraseWaitLoop; 
  /* End erase page. */
                                                             //                 ; Initialize the data pointer 
  0x90, 0xF0, 0x00,                                          //                 MOV DPTR, #0F000H; 
                                                             //                 ; Outer loops 
  0x7F, HIBYTE_WORDS_PER_FLASH_PAGE,                         //                 MOV R7, #imm; 
  0x7E, LOBYTE_WORDS_PER_FLASH_PAGE,                         //                 MOV R6, #imm; 
  0x75, 0xAE, 0x02,                                          //                 MOV FLC, #02H; // WRITE 
                                                             //                     ; Inner loops 
  0x7D, FLASH_WORD_SIZE,                                     // writeLoop:          MOV R5, #imm; 
  0xE0,                                                      // writeWordLoop:          MOVX A, @DPTR; 
  0xA3,                                                      //                         INC DPTR; 
  0xF5, 0xAF,                                                //                         MOV FWDATA, A;  
  0xDD, 0xFA,                                                //                     DJNZ R5, writeWordLoop; 
                                                             //                     ; Wait for completion 
  0xE5, 0xAE,                                                // writeWaitLoop:      MOV A, FLC; 
  0x20, 0xE6, 0xFB,                                          //                     JB ACC_SWBSY, writeWaitLoop; 
  0xDE, 0xF1,                                                //                 DJNZ R6, writeLoop; 
  0xDF, 0xEF,                                                //                 DJNZ R7, writeLoop; 
                                                             //                 ; Done, fake a breakpoint 
  0xA5                                                       //                 DB 0xA5; 
}; 


//! Copies flash buffer to flash.
void cc_write_flash_page(u32 adr){
  //Assumes that page has already been written to XDATA 0xF000
  //debugstr("Flashing 2kb at 0xF000 to given adr.");
  
  if(adr&(FLASHPAGE_SIZE-1)){
    debugstr("Flash page address is not on a multiple of 2kB.  Aborting.");
    return;
  }
  
  //Routine comes next
  //WRITE_XDATA_MEMORY(IN: 0xF000 + FLASH_PAGE_SIZE, sizeof(routine), routine);
  cc_write_xdata(0xF000+FLASHPAGE_SIZE,
		 (u8*) flash_routine, sizeof(flash_routine));
  //Patch routine's third byte with
  //((address >> 8) / FLASH_WORD_SIZE) & 0x7E
  cc_pokedatabyte(0xF000+FLASHPAGE_SIZE+2,
		  ((adr>>8)/FLASH_WORD_SIZE)&0x7E);
  //debugstr("Wrote flash routine.");
  
  
  //MOV MEMCTR, (bank * 16) + 1;
  cmddata[0]=0x75;
  cmddata[1]=0xc7;
  cmddata[2]=0x51;
  cc_debug_instr(3);
  //debugstr("Loaded bank info.");
  
  cc_set_pc(0xf000+FLASHPAGE_SIZE);//execute code fragment
  cc_resume();
  
  //debugstr("Executing.");
  
  
  while(!(cc_read_status()&CC_STATUS_CPUHALTED)){
    P1OUT^=1;//blink LED while flashing
  }
  
  
  //debugstr("Done flashing.");
  
  P1OUT&=~1;//clear LED
}

//! Read the PC
unsigned short cc_get_pc(){
  cmddata[0]=CCCMD_GET_PC; //0x28
  cccmd(1);
  ccread(2);
  
  //Return the word.
  return cmddataword[0];
}

//! Set a hardware breakpoint.
void cc_set_hw_brkpnt(unsigned short adr){
  debugstr("FIXME: This certainly won't work.");
  cmddataword[0]=adr;
  cccmd(2);
  ccread(1);
  return;
}


//! Halt the CPU.
void cc_halt(){
  cmddata[0]=CCCMD_HALT; //0x44
  cccmd(1);
  ccread(1);
  return;
}
//! Resume the CPU.
void cc_resume(){
  cmddata[0]=CCCMD_RESUME; //0x4C
  cccmd(1);
  ccread(1);
  return;
}


//! Step an instruction
void cc_step_instr(){
  cmddata[0]=CCCMD_STEP_INSTR; //0x5C
  cccmd(1);
  ccread(1);
  return;
}

//! Debug an instruction.
void cc_debug_instr(unsigned char len){
  //Bottom two bits of command indicate length.
  unsigned char cmd=CCCMD_DEBUG_INSTR+(len&0x3); //0x54+len
  CCWRITE;
  cctrans8(cmd);  //Second command code
  cccmd(len&0x3); //Command itself.
  ccread(1);
  return;
}

//! Debug an instruction, for local use.
unsigned char cc_debug(unsigned char len,
	      unsigned char a,
	      unsigned char b,
	      unsigned char c){
  unsigned char cmd=CCCMD_DEBUG_INSTR+(len&0x3);//0x54+len
  CCWRITE;
  cctrans8(cmd);
  if(len>0)
    cctrans8(a);
  if(len>1)
    cctrans8(b);
  if(len>2)
    cctrans8(c);
  CCREAD;
  return cctrans8(0x00);
}

//! Fetch a byte of code memory.
unsigned char cc_peekcodebyte(unsigned long adr){
  /** See page 9 of SWRA124 */
  unsigned char bank=adr>>15,
    lb=adr&0xFF,
    hb=(adr>>8)&0x7F,
    toret=0;
  adr&=0x7FFF;
  
  //MOV MEMCTR, (bank*16)+1
  cc_debug(3, 0x75, 0xC7, (bank<<4) + 1);
  //MOV DPTR, address
  cc_debug(3, 0x90, hb, lb);
  
  //for each byte
  //CLR A
  cc_debug(2, 0xE4, 0, 0);
  //MOVC A, @A+DPTR;
  toret=cc_debug(3, 0x93, 0, 0);
  //INC DPTR
  //cc_debug(1, 0xA3, 0, 0);
  
  return toret;
}


//! Set a byte of data memory.
unsigned char cc_pokedatabyte(unsigned int adr,
			   unsigned char val){
  unsigned char
    hb=(adr&0xFF00)>>8,
    lb=adr&0xFF;
  
  //MOV DPTR, adr
  cc_debug(3, 0x90, hb, lb);
  //MOV A, val
  cc_debug(2, 0x74, val, 0);
  //MOVX @DPTR, A
  cc_debug(1, 0xF0, 0, 0);
  
  return 0;
  /*
DEBUG_INSTR(IN: 0x90, HIBYTE(address), LOBYTE(address), OUT: Discard);
for (n = 0; n < count; n++) {
    DEBUG_INSTR(IN: 0x74, inputArray[n], OUT: Discard);
    DEBUG_INSTR(IN: 0xF0, OUT: Discard);
    DEBUG_INSTR(IN: 0xA3, OUT: Discard);
}
   */
}

//! Fetch a byte of data memory.
unsigned char cc_peekdatabyte(unsigned int adr){
  unsigned char
    hb=(adr&0xFF00)>>8,
    lb=adr&0xFF,
    toret;
  
  //MOV DPTR, adr
  cc_debug(3, 0x90, hb, lb);
  //MOVX A, @DPTR
  //Must be 2, perhaps for clocking?
  return cc_debug(3, 0xE0, 0, 0);
}


//! Fetch a byte of IRAM.
u8 cc_peekirambyte(u8 adr){
  //CLR A
  cc_debug(2, 0xE4, 0, 0);
  //MOV A, #iram
  return cc_debug(3, 0xE5, adr, 0);
}

//! Write a byte of IRAM.
u8 cc_pokeirambyte(u8 adr, u8 val){
  //CLR A
  cc_debug(2, 0xE4, 0, 0);
  //MOV #iram, #val
  return cc_debug(3, 0x75, adr, val);
  //return cc_debug(3, 0x75, val, adr);
}


