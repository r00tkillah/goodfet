GoodFET Firmware
by Travis Goodspeed
<travis at radiantmachines.com>

Requires MSPGCC and msp430-bsl.

Assumes MSP430F161x by default.  Call for others by the following method,
recognizing that 2618 support is a rather recent addition and only works
in MSPGCC from CVS.

export mcu=msp430x2618
make -e



Some weird switches,
1) Build for a static DCO configuration.  Useful for standalone firmware.
CFLAGS="-DSTATICDCO=0x8F9E" make clean all
