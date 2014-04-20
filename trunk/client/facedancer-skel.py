#!/usr/bin/env python3
from serial import Serial, PARITY_NONE

from Facedancer import *
from MAXUSBApp import *
from USBSkel import *


sp = GoodFETSerialPort()
fd = Facedancer(sp, verbose=1)
u = MAXUSBApp(fd, verbose=1)

d = USBSkelDevice(u, verbose=3)

d.connect()

try:
    d.run()
except KeyboardInterrupt:
    d.disconnect()
