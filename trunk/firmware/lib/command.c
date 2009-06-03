//! Different command handling functions.

unsigned char cmddata[256];

//!Transmit data.
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
