
PORT=/dev/ttyUSB0
BSL=tos-bsl --invert-reset --invert-test -c $(PORT)

#mcu=msp430x1611
mcu=msp430x1612

#ldscript is wonky
GCCINC=-T ../../ldscripts/161x.x

CC=msp430-gcc -g -mmcu=$(mcu) -DGCC $(GCCINC) -I ../../include

libs=../../lib/msp430f1612.c
app=echo

install: $(app)
	$(BSL) -e -p $(app) 
	#$(BSL) -P $(app) -g 0x2500
	$(BSL) -P $(app) -r
$(app): $(app).c $(libs)
erase:
	$(BSL) -e 
clean:
	rm -f $(app)
