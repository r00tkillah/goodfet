/*! \file dspic33f.c

  \author Scott Livingston

  \brief dsPIC33F programmer application for the GoodFET. Structure
         and style is somewhat modeled after avr.c

  \date March-May 2010
*/


#include "apps.h"
#include "platform.h"
#include "command.h"

#include "dspic33f.h"


void pic33f_setup()
{
	// Initialize pins; do NOT begin transaction.
	P5DIR |= PGC|MCLR;
	P5REN &= ~(PGC|PGD|MCLR);
	DIR_PGD_WR; // Initially PGD in write mode

	SET_MCLR;
	CLR_PGC;
	CLR_PGD;

	prep_timer(); // What better time than now?
}


//! Handle a PIC command; currently assumes dsPIC33F/PIC24H
void pichandle( unsigned char app,
				unsigned char verb,
				unsigned long len )
{
	unsigned int nb; // Number of bytes
	unsigned int highb, loww; // Used for ICSP commands

	switch (verb) {

	case PIC_DEVID33F:
		nb = pic33f_getid();
		txdata(app,verb,nb);
		break;

	case PIC_SIX33F:
		loww = *cmddata;
		loww |= (*(cmddata+1)) << 8;
		highb = *(cmddata+2);
		pic33f_six( highb, loww );
		txdata(app,verb,0);
		break;

	case PIC_SIXLIST33F:
		pic33f_sixlist( len ); // Reply to host is handled by pic33f_sixlist.
		break;

	case PIC_REGOUT33F:
		loww = pic33f_regout();
		*cmddata = loww & 0xff;
		*(cmddata+1) = loww >> 8;
		txdata(app,verb,2);
		break;

	case PIC_RESET33F:
		CLR_MCLR;
		delay_ms(20);
		SET_MCLR;
		break;

	case PIC_START33F:
		pic33f_connect();
		txdata(app,verb,0);
		break;

	case PIC_STOP33F:
		pic33f_disconnect();
		txdata(app,verb,0);
		break;

	default:
		debugstr( "Verb unimplemented in PIC application." );
		txdata(app,NOK,0);
		break;

	}
}


void pic33f_trans8( unsigned char byte )
{
	/* We only twiddle the PGD and PGC lines.
	   MCLR is assumed to be in the correct state. */
	unsigned int i;
	
	DIR_PGD_WR; // Write mode
	i = 1;
	while (i & 0xff) {
		if (byte & i) {
			SET_PGD;
		} else {
			CLR_PGD;
		}
		delay_ticks(10);
		SET_PGC;
		delay_ticks(10);

		CLR_PGC;
		delay_ticks(10);
		i = i << 1;
	}
	CLR_PGD;
	DIR_PGD_RD; // Read mode
}

void pic33f_trans16( unsigned int word )
{
	pic33f_trans8( word & 0xff );
	pic33f_trans8( word >> 8 );
}


void pic33f_six( unsigned int highb, unsigned int loww )
{
	/* dsPIC33F/PIC24H instructions have width 24 bits, so we use the
	   lower 8 bits of highb and (all 16 bits of) loww to form the
	   instruction.

	   Shift in the instruction.  Note that it does not execute until
	   the next 4 clock cycles (which also corresponds to a command
	   receipt time). */
	unsigned int i;
	DIR_PGD_WR;
	CLR_PGD;
	CLR_PGC;
	for (i = 0; i < 4; i++) {
		SET_PGC;
		delay_ticks(10);
		CLR_PGC;
		delay_ticks(10);
	}
	pic33f_trans16( loww );
	pic33f_trans8( highb );
	DIR_PGD_RD;
}


unsigned int pic33f_regout()
{	
	unsigned int i;
	unsigned int result = 0x0000;

	DIR_PGD_WR;
	
	// Shift in command (REGOUT: 0001b).
	SET_PGD;
	delay_ticks(10);
	SET_PGC;
	delay_ticks(10);
	CLR_PGC;
	delay_ticks(10);
	
	CLR_PGD;
	delay_ticks(10);
	for (i = 0; i < 3; i++) {
		SET_PGC;
		delay_ticks(10);
		CLR_PGC;
		delay_ticks(10);
	}

	// Pump clock for 8 cycles, and switch PGD direction to read.
	for (i = 0; i < 7; i++) {
		SET_PGC;
		delay_ticks(10);
		CLR_PGC;
		delay_ticks(10);
	}
	DIR_PGD_RD;

	/* Now read VISI register (LSb first, as usual).
       Note that when reading from attached device, data is valid (to
	   be read) on falling clock edges. */
	for (i = 0; i < 16; i++) {
		SET_PGC;
		delay_ticks(10);
		CLR_PGC;
		result |= READ_PGD << i;
		delay_ticks(10);
	}

	/* One last tick apparently is needed here, at least by the
	   dsPIC33FJ128GP708 chip that I am working with. Note that this
	   is not in the flash programming specs. */
	SET_PGC; 
	delay_ticks(10);
	CLR_PGC;
	delay_ticks(10);

	return result;
}


void pic33f_sixlist( unsigned int list_len )
{
	unsigned int k;
	unsigned int instr_loww;

	// Bound to Rx buffer size.
	if (list_len > CMDDATALEN)
		list_len = CMDDATALEN;

	// Run each instruction!
	for (k = 0; k < list_len-2; k+=3) {
		instr_loww = *(cmddata+k);
		instr_loww |= (*(cmddata+k+1)) << 8;
		pic33f_six( *(cmddata+k+2), instr_loww );
	}

	// Reply with total number of bytes used from Rx buffer.
	txdata( PIC, PIC_SIXLIST33F, k );
}


unsigned int pic33f_getid()
{
	unsigned int result;
	unsigned int nb = 0;

	pic33f_connect();

	// Read application ID.
	pic33f_six( 0x04, 0x0200 ); // goto 0x200 (i.e. reset)
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0x20, 0x0800 ); // mov #0x80, W0
	pic33f_six( 0x88, 0x0190 ); // mov W0, TBLPAG
	pic33f_six( 0x20, 0x7F00 ); // mov #0x7F0, W0
	pic33f_six( 0x20, 0x7841 ); // mov #VISI, W1
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0xBA, 0x0890 ); // TBLRDL [W0], [W1]
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0x00, 0x0000 ); // nop
	result = pic33f_regout();
	*cmddata = result & 0xff;
	nb += 1;

	// Read DEVID.
	pic33f_six( 0x20, 0x0FF0 ); // mov #0xFF, W0
	pic33f_six( 0x88, 0x0190 ); // mov W0, TBLPAG
	pic33f_six( 0xEB, 0x0000 ); // clr W0
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0xBA, 0x08B0 ); // TBLRDL [W0++], [W1]
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0x00, 0x0000 ); // nop
	result = pic33f_regout();
	*(cmddata+1) = result & 0xff;
	*(cmddata+2) = result >> 8;
	nb += 2;

	// Read hardware revision.
	pic33f_six( 0xBA, 0x0890 ); // TBLRDL [W0++], [W1]
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0x00, 0x0000 ); // nop
	result = pic33f_regout();
	*(cmddata+3) = result & 0xff;
	*(cmddata+4) = result >> 8;
	nb += 2;

	pic33f_disconnect();

	return nb;
}


void pic33f_connect()
{
	unsigned int key_low;
	unsigned int key_high;

	key_low = ICSP_KEY_LOW;
	key_high = ICSP_KEY_HIGH;

	pic33f_setup();

	CLR_PGC;
	delay_us(1);
	
	CLR_MCLR;
	delay_ms(3);
	SET_MCLR;
	delay_us(200);
	CLR_MCLR;
	delay_us(10);
	
	// Enter ICSP key
	pic33f_trans8( key_low & 0xff );
	key_low = key_low >> 8;
	pic33f_trans8( key_low & 0xff );
	pic33f_trans8( key_high & 0xff );
	key_high = key_high >> 8;
	pic33f_trans8( key_high & 0xff );

	delay_us(1);
	SET_MCLR; // ...and pull MCLR pin back up.
	delay_ms(25); // Now wait about 25 ms (required per spec!).

	/* The first ICSP command must be a SIX, and further, 9 bits are
       required before the instruction (to be executed), rather than
       the typical 4 bits. Thus, to simplify code, I simply load a nop
       here; hence 33 bits are shifted into the dsPIC33F/PIC24H. */
	DIR_PGD_WR;
	CLR_PGD;
	CLR_PGC;
	for (key_low = 0; key_low < 33; key_low++) {
		SET_PGC;
		delay_us(1);
		CLR_PGC;
		delay_us(1);
	}
	DIR_PGD_RD;

}


void pic33f_disconnect()
{
	DIR_PGD_WR;
	CLR_PGD;
	CLR_PGC;
	delay_ms(10);
	CLR_MCLR;
}
