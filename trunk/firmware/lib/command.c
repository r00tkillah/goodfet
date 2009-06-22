//! Different command handling functions.

unsigned char cmddata[256];

//! Transmit a string.
void txstring(unsigned char app,
	      unsigned char verb,
	      const char *str){
  unsigned char len=strlen(str);
  serial_tx(app);
  serial_tx(verb);
  serial_tx(len);
  while(len--)
    serial_tx(*(str++));
}

//! Transmit data.
void txdata(unsigned char app,
	    unsigned char verb,
	    unsigned char len){
  unsigned int i=0;
  serial_tx(app);
  serial_tx(verb);
  serial_tx(len);
  for(i=0;i<len;i++){
    serial_tx(cmddata[i]);
  }
}

//! Delay for a count.
void delay(unsigned int count){
  volatile unsigned int i=count;
  while(i--) asm("nop");
}
