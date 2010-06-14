
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
CC=msp430-gcc -Wall -Os -g -mmcu=$(mcu) -D$(mcu) -Dplatform=$(platform) -DGCC $(GCCINC) -I include $(CCEXTRA)

#Define extra modules here.
#moreapps?=apps/i2c/i2c.o  apps/glitch/glitch.o apps/jtag/sbw.o apps/smartcard/smartcard.o apps/jtag/ejtag.o apps/jtag/jtagxscale.o
moreapps?=apps/jtag/sbw.o
# should include apps/jtag/jtagarm7tdmi.o to build jtag for ARM7
# should include apps/pic/dspic33f.o to build support for PIC24H/dsPIC33F

apps= $(moreapps) apps/chipcon/chipcon.o apps/radios/nrf.o apps/monitor/monitor.o apps/spi/spi.o   apps/jtag/jtag.o apps/jtag/jtag430.o apps/jtag/jtag430x2.o apps/avr/avr.o 

#apps/chipcon/chipconasm.o removed
libs= lib/$(mcu).o lib/command.o apps/jtag/jtag430asm.o  lib/dco_calib.o

app= goodfet

all: $(app).hex

lib/.o:
	./configure
	false
lib/RUNCONFIG.o:
	./configure
	false
include/config.h:
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
.FAKE: docs include/config.h
