GoodFET Firmware
by Travis Goodspeed <travis at radiantmachines.com>
and some good neighbors.

Set $GOODFET to be the port of your GoodFET, such as
export GOODFET=/dev/cu.usbserial-*      #Darwin
export GOODFET=/dev/ttyUSB*             #Linux (Default)

The target board must be specified.  For example,
board=goodfet31 make clean install
board=goodfet41 make clean install
board=telosb make clean install

We require at least msp430-gcc-4.4.5, but older versions might work if
you're lucky.
