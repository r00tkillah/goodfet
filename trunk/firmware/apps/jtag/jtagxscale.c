/*! 
  \file jtagxscale.c
  \author Dave Huseby <dave@linuxprogrammer.org>
  \brief Intel XScale JTAG
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"
#include "jtagxscale.h"

/* From the Intel XScale Core Developer's Manual:
 *
 * The Intel XScale® core provides test features compatible with IEEE Standard
 * Test Access Port and Boundary Scan Architecture (IEEE Std. 1149.1). These 
 * features include a TAP controller, a 5 or 7 bit instruction register, and 
 * test data registers to support software debug. The size of the instruction 
 * register depends on which variant of the Intel XScale® core is being used.
 * This can be found out by examining the CoreGen field of Coprocessor 15, ID 
 * Register (bits 15:13). (See Table 7-4, "ID Register" on page 7-81 for more 
 * details.) A CoreGen value of 0x1 means the JTAG instruction register size 
 * is 5 bits and a CoreGen value of 0x2 means the JTAG instruction register 
 * size is 7 bits.
 *
 */

/* NOTE: I heavily cribbed from the ARM7TDMI jtag implementation. Credit where
 * credit is due. */

/* this handles shifting arbitrary length bit strings into the instruction
 * register and clocking out bits while leaving the JTAG state machine in a
 * known state. it also handle bit swapping. */
unsigned long jtag_xscale_shift_n(unsigned long word,
                                  unsigned char nbits,
                                  unsigned char flags)
{
    unsigned int bit;
    unsigned long high = 1;
    unsigned long mask;

    for (bit = (nbits - 1) / 8; bit > 0; bit--)
        high <<= 8;
    
    high <<= ((nbits - 1) % 8);

    mask = high - 1;

    if (flags & LSB) 
    {
        /* clock the bits into the IR from LSB to MSB order */
        for (bit = nbits; bit > 0; bit--) 
        {
            /* write MOSI on trailing edge of previous clock */
            if (word & 1)
            {
                SETMOSI;
            }
            else
            {
                CLRMOSI;
            }
            word >>= 1;

            if (bit == 1 && !(flags & NOEND))
                SETTMS; /* TMS high on last bit to exit. */

            /* tick tock the clock line */
            XTT;

            /* read MISO on trailing edge */
            if (READMISO)
            {
                word += (high);
            }
        }
    } 
    else 
    {
        /* clock the bits into the IR from MSB to LSB order */
        for (bit = nbits; bit > 0; bit--) 
        {
            /* write MOSI on trailing edge of previous clock */
            if (word & high)
            {
                SETMOSI;
            }
            else
            {
                CLRMOSI;
            }
            word = (word & mask) << 1;

            if (bit == 1 && !(flags & NOEND))
                SETTMS;//TMS high on last bit to exit.

            /* tick tock the clock line */
            XTT;

            /* read MISO on trailing edge */
            word |= (READMISO);
        }
    }

    SETMOSI;

    if (!(flags & NOEND))
    {
        /* exit state */
        XTT;

        /* update state */
        if (!(flags & NORETIDLE))
        {
            CLRTMS;
            XTT;
        }
    }

    return word;
}


/* this handles shifting in the IDCODE instruction and shifting the result
 * out the TDO and return it. */
unsigned long jtag_xscale_idcode()
{
    /* NOTE: this assumes that we're in the run-test-idle state */

    /* get into the shift-ir state */
    SHIFT_IR;

    /* shift the ID code instruction into the IR and return to run-test-idle */
    jtag_xscale_shift_n(XSCALE_IR_IDCODE, 5, LSB);

    /* get into the shift-dr state */
    SHIFT_DR;

    /* now clock out the 32 bit ID code and return back to run-test-idle */
    return jtag_xscale_shift_n(0, 32, LSB);
}

/* Handles XScale JTAG commands.  Forwards others to JTAG. */
void xscalehandle(unsigned char app,
                  unsigned char verb,
                  unsigned long len)
{    
    switch(verb) 
    {
        /*
         * Standard Commands
         */
        case SETUP:

            /* set up the pin I/O for JTAG */
            jtagsetup();

            /* reset to run-test-idle state */
            RUN_TEST_IDLE;

            /* send back OK */
            txdata(app, OK, 0);

            break;

        case START:
        case STOP:
        case PEEK:
        case POKE:
        case READ:
        case WRITE:
        default:
 
            /* send back OK */
            txdata(app, OK, 0);

            break;

        /*
         * XScale Commands
         */
        case XSCALE_GET_CHIP_ID:

            /* reset to run-test-idle state */
            RUN_TEST_IDLE;

            /* put the ID code in the data buffer */
            cmddatalong[0] = jtag_xscale_idcode();

            /* send it back to the client */
            txdata(app,verb,4);

            break;
    }
}
