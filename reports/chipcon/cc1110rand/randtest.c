#include <cc1110.h>

#include "randtest.h"

#define u8 unsigned char
#define u16 unsigned int


int rndu16();
void initrnd();

//! Get a random byte from the LFSR.
u8 halRfGetRandomByte(void){
  return rndu16();
}


#define BYTECOUNT 64

u16 randcode, randcount;
u8 rands[BYTECOUNT];
void main(){
  long a;
  
  //Seems to seed with zeroes.
  initrnd();
  
  randcount=0;
  while(1){
    //Data is invalid.
    randcode=0xdead;
    
    for(a=0;a<BYTECOUNT;a++)
      //Uncomment one of the following lines.
      //rands[a]=ADCTSTL;
      rands[a]=halRfGetRandomByte();
    
    //Data is valid.
    randcode=0xbeef;
    
    //Soft Break
    _asm
      .byte 0xa5
      _endasm;
    randcount++;
  }
}
