/*! \file jtag430x2.c
  \author Travis Goodspeed <travis at radiantmachines.com>
  \brief MSP430X2 JTAG (20-bit)
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"

unsigned char jtagid;

//! Get the JTAG ID
unsigned char jtag430x2_jtagid(){
  jtag430_resettap();
  return jtagid=jtag_ir_shift8(IR_BYPASS);
}
//! Start JTAG, take pins
unsigned char jtag430x2_start(){
  jtagsetup();
  
  //Known-good starting position.
  //Might be unnecessary.
  SETTST;
  SETRST;
  
  delay(0xFFFF);
  
  //Entry sequence from Page 67 of SLAU265A for 4-wire MSP430 JTAG
  CLRRST;
  delay(10);//10
  CLRTST;

  delay(5);//5
  SETTST;
  msdelay(5);//5
  SETRST;
  P5DIR&=~RST;
  
  delay(0xFFFF);
  
  //Perform a reset and disable watchdog.
  return jtag430x2_jtagid();
}

//! Grab the core ID.
unsigned int jtag430_coreid(){
  jtag_ir_shift8(IR_COREIP_ID);
  return jtag_dr_shift16(0);
}

//! Grab the device ID.
unsigned long jtag430_deviceid(){
  jtag_ir_shift8(IR_DEVICE_ID);
  return jtag_dr_shift20(0);
}


//! Write data to address
void jtag430x2_writemem(unsigned long adr,
			unsigned int data){
  jtag_ir_shift8(IR_CNTRL_SIG_CAPTURE);
  if(jtag_dr_shift16(0) & 0x0301){
    CLRTCLK;
    jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
    if(adr>=0x100)
      jtag_dr_shift16(0x0500);//word mode
    else
      jtag_dr_shift16(0x0510);//byte mode
    jtag_ir_shift8(IR_ADDR_16BIT);
    jtag_dr_shift20(adr);
    
    SETTCLK;
    
    jtag_ir_shift8(IR_DATA_TO_ADDR);
    jtag_dr_shift16(data);//16 word

    CLRTCLK;
    jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
    jtag_dr_shift16(0x0501);
    SETTCLK;

    CLRTCLK;
    SETTCLK;
    //init state
  }else{
    while(1) P1OUT^=1; //loop if locked up
  }
}

//! Read data from address
unsigned int jtag430x2_readmem(unsigned long adr){
  unsigned int toret=0;
  //unsigned int tries=5;
  
  while(1){
    do{
      jtag_ir_shift8(IR_CNTRL_SIG_CAPTURE);
    }while(!(jtag_dr_shift16(0) & 0x0301));
    
    if(jtag_dr_shift16(0) & 0x0301){
      // Read Memory
      CLRTCLK;
      jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
      if(adr>=0x100){
	jtag_dr_shift16(0x0501);//word read
      }else{
	jtag_dr_shift16(0x0511);//byte read
      }
      
      jtag_ir_shift8(IR_ADDR_16BIT);
      jtag_dr_shift20(adr); //20
      
      jtag_ir_shift8(IR_DATA_TO_ADDR);
      SETTCLK;
      CLRTCLK;
      toret = jtag_dr_shift16(0x0000);
      
      SETTCLK;
      
      //Cycle a bit.
      CLRTCLK;
      SETTCLK;
      return toret;
    }
  }
  //return toret;
}

//! Syncs a POR.
unsigned int jtag430x2_syncpor(){
  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x1501); //JTAG mode
  while(!(jtag_dr_shift16(0) & 0x200));
  return jtag430x2_por();
}

//! Executes an MSP430X2 POR
unsigned int jtag430x2_por(){
  unsigned int i = 0;
  
  // tick
  CLRTCLK;
  SETTCLK;

  jtag_ir_shift8(IR_CNTRL_SIG_16BIT);
  jtag_dr_shift16(0x0C01);
  jtag_dr_shift16(0x0401);
  
  //cycle
  for (i = 0; i < 10; i++){
    CLRTCLK;
    SETTCLK;
  }
  
  jtag_dr_shift16(0x0501);
  
  // tick
  CLRTCLK;
  SETTCLK;
  
  
  // Disable WDT
  jtag430x2_writemem(0x015C, 0x5A80);
  
  // check state
  jtag_ir_shift8(IR_CNTRL_SIG_CAPTURE);
  if(jtag_dr_shift16(0) & 0x0301)
    return(1);//ok
  
  return 0;//error
}


//! Check the fuse.
unsigned int jtag430x2_fusecheck(){
  int i;
  for(i=0;i<3;i++){
    jtag_ir_shift8(IR_CNTRL_SIG_CAPTURE);
    if(jtag_dr_shift16(0xAAAA)==0x5555)
      return 1;//blown
  }
  return 0;//unblown
}


//! Handles MSP430X2 JTAG commands.  Forwards others to JTAG.
void jtag430x2handle(unsigned char app,
		     unsigned char verb,
		     unsigned char len){
  register char blocks;
  
  unsigned int i,val;
  unsigned long at;
  
  //jtag430_resettap();
  
  if(verb!=START && jtag430mode==MSP430MODE){
    jtag430handle(app,verb,len);
    return;
  }
  
  switch(verb){
  case START:
    //Enter JTAG mode.
    //do 
      cmddata[0]=jtag430x2_start();
    //while(cmddata[0]==00 || cmddata[0]==0xFF);
    
    //MSP430 or MSP430X
    if(jtagid==MSP430JTAGID){ 
      jtag430mode=MSP430MODE;
      drwidth=16;
      jtag430_resettap();
      txdata(app,verb,1);
      return;
    }else if(jtagid==MSP430X2JTAGID){
      jtag430mode=MSP430X2MODE;
      drwidth=20;
    }else{
      txdata(app,NOK,1);
      return;
    }
    
    jtag430x2_fusecheck();
        
    jtag430x2_syncpor();
    
    jtag430_resettap();
    
    txdata(app,verb,1);
    break;
  case JTAG430_READMEM:
  case PEEK:
    blocks=(len>4?cmddata[4]:1);
    at=cmddatalong[0];
    
    /*
    cmddataword[0]=jtag430x2_readmem(at);
    txdata(app,verb,2);
    break;
    */
    
    len=0x80;
    serial_tx(app);
    serial_tx(verb);
    serial_tx(len);
    
    while(blocks--){
      for(i=0;i<len;i+=2){
	jtag430_resettap();
	delay(10);
	
	val=jtag430x2_readmem(at);
		
	at+=2;
	serial_tx(val&0xFF);
	serial_tx((val&0xFF00)>>8);
      }
    }
    
    break;
  case JTAG430_COREIP_ID:
    cmddataword[0]=jtag430_coreid();
    txdata(app,verb,2);
    break;
  case JTAG430_DEVICE_ID:
    cmddatalong[0]=jtag430_deviceid();
    txdata(app,verb,4);
    break;

  case JTAG430_WRITEMEM:
  case POKE:
    jtag430x2_writemem(cmddatalong[0],
		       cmddataword[2]);
    cmddataword[0]=jtag430x2_readmem(cmddatalong[0]);
    txdata(app,verb,2);
    break;

    //unimplemented functions
  case JTAG430_HALTCPU:  
  case JTAG430_RELEASECPU:
  case JTAG430_SETINSTRFETCH:
  case JTAG430_WRITEFLASH:
  case JTAG430_ERASEFLASH:
  case JTAG430_SETPC:
    txdata(app,NOK,0);
    break;
  default:
    jtaghandle(app,verb,len);
  }
  jtag430_resettap();
}
