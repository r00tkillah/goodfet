#!/bin/zsh
(
cd ../trunk/firmware && make clean install
for GOODFET in /dev/ttyUSB*; make install
)