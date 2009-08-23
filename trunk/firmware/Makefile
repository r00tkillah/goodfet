
PORT=/dev/ttyUSB0
BSL=msp430-bsl --invert-reset --invert-test -c $(PORT) --speed=38400

#mcu=msp430x2618
mcu=msp430x1612


#N.B., gcc WILL NOT BITCH if this file doesn't exist.
#GCCINC=-T ldscripts/161x.x
GCCINC=-T ldscripts/$(mcu).x

CC=msp430-gcc -Wall -g -mmcu=$(mcu) -DGCC $(GCCINC) -I include

apps= apps/monitor/monitor.o apps/spi/spi.o apps/i2c/i2c.o apps/chipcon/chipcon.o apps/jtag/jtag.o apps/jtag/jtag430.o
libs= lib/$(mcu).o lib/command.o apps/jtag/jtag430asm.o
app=goodfet

all: $(app).hex

goodfet.hex: goodfet

run:
	../client/goodfet.msp430 test

install: $(app).hex
	$(BSL) -e -p $(app).hex 
verify:
	$(BSL) -P $(app).hex -v $(app).hex
$(app): $(app).c $(libs) $(apps)
$(app).hex: $(app)
	msp430-objcopy goodfet -O ihex goodfet.hex
m4s: $(app).hex
	msp430-objdump -D -m msp430 $(app).hex | m4s init
erase:
	$(BSL) -e 
clean:
	rm -f $(app) $(app).hex $(libs) $(apps)
