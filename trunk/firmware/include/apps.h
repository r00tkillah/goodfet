/*! \file apps.h
  \author Travis Goodspeed
  \brief Application definitions.
*/

//Essential and highly standardized stuff in 0x00 range.
#define MONITOR 0x00
#define SPI 0x01
#define I2CAPP 0x02

//All JTAG targets in 0x10 range.
#define JTAG 0x10
#define JTAG430 0x11
#define EJTAG 0x12
#define JTAGARM7TDMI 0x13 //Uncomment this as soon as client patched.

//Manufacturer-specific protocols go in 0x30 and 0x40.
#define CHIPCON 0x30
#define SIF 0x31
#define AVR 0x32
#define PIC 0x34

//Radio peripherals are in the 0x50 range.
#define NRF 0x50

//Keep 0x60 empty for now.

//Weird stuff in 0x70 range.
#define OCT 0x70
#define GLITCH 0x71
#define PLUGIN 0x72
#define SMARTCARD 0x73

#define RESET 0x80	// not a real app -- causes firmware to reset

#define DEBUGAPP 0xFF
