#!/bin/zsh

cd ../trunk/firmware && make clean install
for GOODFET in /dev/ttyUSB0; (cd ../trunk/firmware && make install)