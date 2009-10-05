#!/bin/zsh

# Testing script for the GoodFET Chipcon Client.

../trunk/client/goodfet.cc info
../trunk/client/goodfet.cc test

#Verify read/write of RAM.
../trunk/client/goodfet.cc pokedata 0xffe0 0xde
../trunk/client/goodfet.cc pokedata 0xffe1 0xad
../trunk/client/goodfet.cc pokedata 0xffe2 0xbe
../trunk/client/goodfet.cc pokedata 0xffe3 0xef
../trunk/client/goodfet.cc peekdata 0xffe0 0xffe3
