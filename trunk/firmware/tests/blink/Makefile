
PORT=/dev/ttyUSB0
BSL=tos-bsl --invert-reset --invert-test -c $(PORT)

#mcu=msp430x1611
mcu=msp430x1612

CC=msp430-gcc -g -mmcu=$(mcu) -DGCC

app=blink

install: $(app)
	$(BSL) -e -p $(app) 
	#$(BSL) -P $(app) -g 0x2500
	$(BSL) -P $(app) -r
erase:
	$(BSL) -e 
