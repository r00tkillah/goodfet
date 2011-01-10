
#include `uname`.mak
#GOODFET?=/dev/ttyUSB0

#For tos-bsl, use --invert-reset --invert-test
BSL?=goodfet.bsl --speed=38400

#One of these should be defined explicitly.
#Default removed because of confusion.

#mcu=msp430x2274
#mcu=msp430x2618
#mcu?=msp430x1612
mcu?=RUNCONFIG

#platform=goodfet
#platform=telosb
#platform=z1
platform?=goodfet

#N.B., gcc WILL NOT BITCH if this file doesn't exist.
#GCCINC=-T ldscripts/161x.x
GCCINC=-T ldscripts/$(mcu).x

CCEXTRA?=
CC=msp430-gcc -Wall -Os -g -mmcu=$(mcu) -D$(mcu) -D$(platform) -Dplatform=$(platform) -DGCC $(GCCINC) -I include $(CCEXTRA)

# Available Applications
# ======================
# Below is a list of available applications and their descriptions.

# PRODUCTION: 
# None have made it to production grade quality

# BETA:
# monitor -- Basic monitor
# spi -- Turns GF into USB-to-SPI adapter
# jtag -- Low level JTAG (needed by all other JTAG code)
# sbw -- Makes JTAG Spy-by-wire multiplexable

# ALPHA:
# jtag430 -- 16-bit MSP430 JTAG
# jtag430x2 -- 20-bit MSP430 JTAG

# PRE-ALPHA:
#  Bus protocols:
# i2c -- Turns GF into USB-to-i2c adapter
# jtagarm7 -- ARM7TDMI JTAG
# ejtag -- MIPS JTAG
# jtagxscale -- XScale JTAG

#  Microcontrollers:
# chipcon -- Chipcon radio 8051 debugging
# avr -- AVR debugger
# dspic -- PIC24H/dsPIC33F debugger
# adc -- ADC10 (still specific to x2274, GoodFET32)

#  Radios:
# nrf -- Nordic RF SPI
# ccspi -- Chipcon SPI

# Miscelaneous:
# glitch -- Glitch research tool
# smartcard -- Smartcard IO


# Configurations
# ==============
# This is what you need to customize to specify which apps you want in your
# firmware.  The "config" variable is just a space-delimited list of apps you
# want included.  The makefile will take the list of apps and include all of
# the proper code needed to build your desired firmware.

# bare minimum
# config = monitor

# basic JTAG adapter
# config = monitor jtag

# Chipcon hacking
# config = monitor chipcon ccspi

# Glitch research
# config = monitor glitch

# XScale PXA255 JTAG
# config = monitor jtagxscale

# Old Default Config
config = monitor sbw glitch chipcon nrf ccspi spi jtagarm7 jtag430 jtag430x2 avr


# Build the needed list of app and lib object files from the config
apps=
libs= lib/$(mcu).o lib/command.o lib/dco_calib.o

# include monitor app
ifeq ($(filter monitor, $(config)), monitor)
	apps+= apps/monitor/monitor.o
endif

# include spi app
ifeq ($(filter spi, $(config)), spi)
	apps+= apps/spi/spi.o
endif

# include base jtag if they specified it explicitly
ifeq ($(filter jtag, $(config)), jtag)
	ifneq ($(filter apps/jtag/jtag.o, $(apps)), apps/jtag/jtag.o)
		apps+= apps/jtag/jtag.o
	endif
endif

# include the sbw defs if they specified it
ifeq ($(filter sbw, $(config)), sbw)
	# if they only specify sbw, include jtag
	ifneq ($(filter apps/jtag/jtag.o, $(apps)), apps/jtag/jtag.o)
		apps+= apps/jtag/jtag.o
	endif
	apps+= apps/jtag/sbw.o
endif

# include jtag430 app
ifeq ($(filter jtag430, $(config)), jtag430)
	# add in base jtag code if not already
	ifneq ($(filter apps/jtag/jtag.o, $(apps)), apps/jtag/jtag.o)
		apps+= apps/jtag/jtag.o
	endif
	# add in the jtag430asm code if needed
	ifneq ($(filter apps/jtag/jtag430asm.o, $(libs)), apps/jtag/jtag430asm.o)
		apps+= apps/jtag/jtag430asm.o
	endif
	apps+= apps/jtag/jtag430.o
endif

# include jtag430x2 app
ifeq ($(filter jtag430x2, $(config)), jtag430x2)
	# add in base jtag code if not already
	ifneq ($(filter apps/jtag/jtag.o, $(apps)), apps/jtag/jtag.o)
		apps+= apps/jtag/jtag.o
	endif
	# add in the jtag430asm code if needed
	ifneq ($(filter jtag430asm.o, $(libs)), jtag430asm.o)
		libs+= apps/jtag/jtag430asm.o
	endif
	apps+= apps/jtag/jtag430x2.o
endif

# include i2c app
ifeq ($(filter i2c, $(config)), i2c)
	apps+= apps/i2c/i2c.o
endif

# include jtagarm7 app
ifeq ($(filter jtagarm7, $(config)), jtagarm7)
	# add in base jtag code if not already
	ifneq ($(filter apps/jtag/jtag.o, $(apps)), apps/jtag/jtag.o)
		apps+= apps/jtag/jtag.o
	endif
	apps+= apps/jtag/jtagarm7.o
endif

# include jtagarm7tdmi app
ifeq ($(filter jtagarm7tdmi, $(config)), jtagarm7tdmi)
	# add in base jtag code if not already
	ifneq ($(filter apps/jtag/jtag.o, $(apps)), apps/jtag/jtag.o)
		apps+= apps/jtag/jtag.o
	endif
	apps+= apps/jtag/jtagarm7tdmi.o
endif

# include ejtag app
ifeq ($(filter ejtag, $(config)), ejtag)
	# add in base jtag code if not already
	ifneq ($(filter apps/jtag/jtag.o, $(apps)), apps/jtag/jtag.o)
		apps+= apps/jtag/jtag.o
	endif
	apps+= apps/jtag/ejtag.o
endif

# include jtagxscale app
ifeq ($(filter jtagxscale, $(config)), jtagxscale)
	# add in base jtag code if not already
	ifneq ($(filter apps/jtag/jtag.o, $(apps)), apps/jtag/jtag.o)
		apps+= apps/jtag/jtag.o
	endif
	apps+= apps/jtag/jtagxscale.o
endif

# include chipcon app
ifeq ($(filter chipcon, $(config)), chipcon)
	apps+= apps/chipcon/chipcon.o
endif

# include avr app
ifeq ($(filter avr, $(config)), avr)
	apps+= apps/avr/avr.o
endif

# include pic app
ifeq ($(filter pic, $(config)), pic)
	apps+= apps/pic/dspic33f.o
endif

# include adc10 app
ifeq ($(filter adc, $(config)), adc)
	ifeq ($(mcu), msp430x2274)
		apps+= apps/pic/dspic33f.o
	else
		ERR= $(error The ADC app only works on GoodFET boards with the msp430x2274 processor)
.PHONY: err
err:;$(ERR)

	endif
endif

# include chipcon radio spi app
ifeq ($(filter ccspi, $(config)), ccspi)
	apps+= apps/radios/ccspi.o
endif

# include nrf app
ifeq ($(filter nrf, $(config)), nrf)
	apps+= apps/radios/nrf.o
endif

# include glitch app
ifeq ($(filter glitch, $(config)), glitch)
	apps+= apps/glitch/glitch.o
endif

# include smartcard app
ifeq ($(filter smartcard, $(config)), smartcard)
	apps+= apps/smartcard/smartcard.o
endif


# Rules

app= goodfet

all: $(app).hex

lib/.o: config
	./configure
	false
lib/RUNCONFIG.o:
	./configure
	false
config:
	cp platforms/$(platform).h include/config.h
goodfet.hex: goodfet

run:
	../client/goodfet.msp430 test

install: $(app).hex
	$(BSL) -e -p $(app).hex 
	ls info.txt && $(BSL) -P $(app).hex -p info.txt || true  #MSP430F2xx targets only, inelegant.
verify:
	$(BSL) -P $(app).hex -v $(app).hex
dumpinfo:
	$(BSL) --dumpinfo
$(app).c: config
$(app): $(app).c $(libs) $(apps)
$(app).hex: $(app)
	msp430-objcopy goodfet -O ihex goodfet.hex
m4s: $(app).hex
	msp430-objdump -D -m msp430 $(app).hex | m4s init
erase:
	$(BSL) -e 
clean:
	rm -f $(app) $(app).hex $(libs) $(apps) include/config.h
docs:
	doxygen
pushdocs: docs
	rsync --exclude .svn -ave ssh doc/html/* travisutk,goodfet@web.sourceforge.net:htdocs/docs/
.FAKE: docs

