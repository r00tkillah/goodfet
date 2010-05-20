/*! \file monitor.h
  \author Travis Goodspeed
  \brief Debug monitor commands.
*/

#ifdef MSP430
#include <signal.h>
#include <io.h>
#include <iomacros.h>
#endif

// Generic Commands

//! Overwrite all of RAM with 0xBEEF, then reboot.
void monitor_ram_pattern();
//! Return the number of contiguous bytes 0xBEEF, to measure RAM usage.
unsigned int monitor_ram_depth();

// Monitor Commands
#define MONITOR_CHANGE_BAUD 0x80
#define MONITOR_ECHO 0x81
#define MONITOR_RAM_PATTERN 0x90
#define MONITOR_RAM_DEPTH 0x91

#define MONITOR_DIR 0xA0
#define MONITOR_OUT 0xA1
#define MONITOR_IN  0xA2

#define MONITOR_SILENT 0xB0
#define MONITOR_CONNECTED 0xB1

#define MONITOR_READBUF 0xC0
#define MONITOR_WRITEBUF 0xC1
#define MONITOR_SIZEBUF 0xC2


