
PORT=/dev/ttyUSB0
BSL=goodfet.bsl

#Default to 2001 with least resources.

#mcu=msp430x1611
#mcu=msp430x2618
mcu?=msp430x2001

#GCCINC=-T ../../ldscripts/161x.x
CC=msp430-gcc -g -mmcu=$(mcu) -DGCC $(GCCINC) -I ../../include

app=blink

all: $(app).hex
$(app).hex: $(app)
	msp430-objcopy $(app) -O ihex $(app).hex
install: $(app).hex
	$(BSL) -e -p $(app).hex 
	$(BSL) -P $(app).hex -r
erase:
	$(BSL) -e 
clean:
	rm -f $(app) $(app).hex
