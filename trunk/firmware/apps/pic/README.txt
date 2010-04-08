PIC programmer
March, April 2010.

Scott Livingston <slivingston AT caltech.edu>


Currently targeted at dsPIC33F/PIC24H chip family and tested on

dsPIC33FJ128GP710,
dsPIC33FJ128GP708

(i.e. similar chip, differing in footprint: former is 100-TQFP, latter
is 80-TQFP).

For the 14-pin GoodFET port (size 2x7), the pinout is
3 -> PGD
5 -> !MCLR
7 -> PGC
2 -> Vcc
9 -> GND

Programming is done over a protocol similar to 2-wire SPI (i.e., MOSI
and MISO are combined into a single data line), where the GoodFET is
the master. Currently only ICSP is supported, i.e., the programming
executive (similar to a bootstrap loader in other architectures) is
ignored, if present. Note that dsPIC33F/PIC24H chips seem to ship
without the programming executive present. Confer Microchip document
"dsPIC33F/PIC24H Flash Programming Specification" (DS70152G).

When receiving from (resp. replying to) host, data on the PGD line is
latched (resp. written) by the dsPIC33f/PIC24H chip on the rising edge
of PGC. A statement to this effect appears as a note in section 5.3,
Chapter 5, of the dsPIC33F/PIC24H Flash Programming Spec.

In the dsPIC33F/PIC24H flash programming spec, there is a typo
regarding verification of the presence of the programming
executive. In Section 5.11, it is stated that an Application ID of
0xBB indicates the programming executive is resident. As of 4 April
2010, the correct App ID is 0xCB, as listed later in the spec
document, Section 7 "Device ID". To dump the device and application
IDs and hardware revision number of an attached dsPIC33F/PIC24H chip,
use the goodfet.pic client:

$ ./goodfet.pic devid


Much more documentation is needed for the programmer and is
forthcoming along with more common tools (e.g. verify programming
results). For now, here are some quick examples. To bulk erase program
memory (this is necessary before programming),

$ ./goodfet.pic erase

Then to program the device with a code file, foo.hex,

$ ./goodfet.pic program foo.hex


A quick visual check of results might be a dump of the first few
instruction words.

$ ./goodfet.pic - 0x200 0x220 pretty

This command prints (24-bit width) contents of program memory at
addresses 0x200 through 0x220 to stdout.


For setting up your development environment, I suggest matt's article
on installing Microchip's GCC port for dsPIC/PIC24 microcontrollers
under GNU/Linux (and almost certainly extends to other Unix-like
environments):

http://www.electricrock.co.nz/blog/2009/08/installing-microchips-c-compiler-for-pic24-mcus-and-dspic-dscs-c30-on-ubuntu-9-04/

The port is called C30 by Microchip.
