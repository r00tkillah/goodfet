
PORT=/dev/ttyUSB0
BSL=tos-bsl --invert-reset --invert-test -c $(PORT)

CC=msp430-gcc -g -mmcu=msp430x1611 -DGCC

app=blink

install: $(app)
	$(BSL) -e -p $(app)
	$(BSL) -P $(app) -g 0x4000
erase:
	$(BSL) -e 
