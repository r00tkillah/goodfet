#!/usr/bin/env python3
#
# usb-test.py

from serial import Serial, PARITY_NONE

from Facedancer import *
from MAXUSBApp import *
from USBKeyboard import *

sp = Serial("/dev/ttyUSB0", 115200, parity=PARITY_NONE, timeout=2)
fd = Facedancer(sp, verbose=1)
u = MAXUSBApp(fd, verbose=1)

d = USBKeyboardDevice(u, verbose=4)

d.connect()

try:
    d.run()
# SIGINT raises KeyboardInterrupt
except KeyboardInterrupt:
    d.disconnect()

