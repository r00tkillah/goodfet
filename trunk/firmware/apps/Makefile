
PORT=/dev/ttyUSB0
BSL=tos-bsl --invert-reset --invert-test -c $(PORT)

#mcu=msp430x1611
mcu=msp430x1612

#ldscript is wonky
GCCINC=-T ../ldscripts/161x.x

CC=msp430-gcc -g -mmcu=$(mcu) -DGCC $(GCCINC) -I ../include

apps= monitor/monitor.c spi/spi.c i2c/i2c.c chipcon/chipcon.c jtag/jtag.c
libs= ../lib/msp430f1612.c ../lib/command.c
app=goodfet

all: $(app)

goodfet.hex: goodfet


install: $(app)
	$(BSL) -e -p $(app) 
	$(BSL) -P $(app) -r
$(app): $(app).c $(libs) $(apps)
$(app).hex: $(app)
	msp430-objcopy goodfet -O ihex goodfet.hex
m4s: $(app).hex
	msp430-objdump -D -m msp430 $(app).hex | m4s init
erase:
	$(BSL) -e 
clean:
	rm -f $(app)
