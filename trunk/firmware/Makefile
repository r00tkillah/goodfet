
PORT=/dev/ttyUSB0
BSL=msp430-bsl --invert-reset --invert-test -c $(PORT) --speed=38400

#mcu=msp430x1611
mcu=msp430x1612

#ldscript is wonky
GCCINC=-T ldscripts/161x.x

CC=msp430-gcc -g -mmcu=$(mcu) -DGCC $(GCCINC) -I include

apps= apps/monitor/monitor.o apps/spi/spi.o apps/i2c/i2c.o apps/chipcon/chipcon.o apps/jtag/jtag.o apps/jtag/jtag430.o
libs= lib/msp430f1612.o lib/command.o apps/jtag/jtag430asm.o
app=goodfet

all: $(app).hex

goodfet.hex: goodfet

run:
	../client/goodfet.msp430 test

install: $(app).hex
	$(BSL) -e -p $(app).hex 
	#$(BSL) -P $(app).hex -r
$(app): $(app).c $(libs) $(apps)
$(app).hex: $(app)
	msp430-objcopy goodfet -O ihex goodfet.hex
m4s: $(app).hex
	msp430-objdump -D -m msp430 $(app).hex | m4s init
erase:
	$(BSL) -e 
clean:
	rm -f $(app) $(app).hex $(libs) $(apps)
