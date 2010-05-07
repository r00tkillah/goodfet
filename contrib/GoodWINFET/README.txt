======================
GoodFET Windows Client
======================

GoodWINFET is being constantly developed by me <q @ theqlabs.com> as a
way for those Windows nerds to enjoy the benefits and beauty of Travis
Goodspeed's open-source JTAG adapter and glitching platform. Initially
it was built with only support for the goodfet.msp430 client forked
from the GoodFET's main branch. This was done to fulfill an immediate
need, however I am currently working on developing a much more
functional and versatile tool for the Windows platform. If you have
any questions, comments or bugs please contact me.

<q @theqlabs.com>

"Remember, if it hadn't been for Q Branch you'd have been dead long
ago." -Q

============
INSTALLATION
============

Currently the GoodWINFET requires everything within the ../Client/dist
directory to function fully.  I will slowly work on doing what I can
to reduce the number of dependencies or at least improve the way in
which they're handled. You obviously already have the SVN checkout,
and there is really nothing to install (yet) just navigate to the
../Client/dist directory and run the following commands:

========
COMMANDS
========

Usage: goodfet.exe verb [objects]

goodfet.exe scan
goodfet.exe test
goodfet.exe dump $foo.hex [0x$start 0x$stop]
goodfet.exe erase
goodfet.exe flash $foo.hex [0x$start 0x$stop]
goodfet.exe verify $foo.hex [0x$start 0x$stop]
goodfet.exe poke 0x$adr 0x$val
goodfet.exe peek 0x$start [0x$stop]
goodfet.exe run

Note: Scan was an option added for the Windows client. It scans all
available COM ports for connections and looks for the GoodFET
device. If it finds it, it will display the COM port number and
hardware ID associated with it. In Linux the /dev/ttyUSB* parameter is
used and this is not needed, so for now it's a Windows only function.

=======
EXAMPLE
=======

If I were you, and I was on Windows trying to use the GoodFET this is
what I would do.

COMMAND: goodfet.exe scan

...
*************
GOODFET FOUND
*************
COM6: (FTDIBUS\COMPORT&VID_0403&PID_6001) -> Ready
...

COMMAND: GOODFET=COM6 goodfet.exe <verb>



