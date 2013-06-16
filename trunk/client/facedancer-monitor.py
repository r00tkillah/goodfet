#!/usr/bin/env python3
#
# monitor-test.py

from serial import Serial, PARITY_NONE

from Facedancer import *

sp = Serial("/dev/ttyUSB0", 115200, parity=PARITY_NONE, timeout=1)
fd = Facedancer(sp)

fd.monitor_app.print_info()
fd.monitor_app.list_apps()

res = fd.monitor_app.echo("I am the very model of a modern major general.")

if res == 0:
    print("echo failed")
else:
    print("echo succeeded")

