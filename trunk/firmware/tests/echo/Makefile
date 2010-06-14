

BSL=goodfet.bsl

#mcu=msp430x1611
mcu?=msp430x2618

#ldscript is wonky
#GCCINC=-T ../../ldscripts/161x.x

CC=msp430-gcc -g -mmcu=$(mcu) -DGCC $(GCCINC) -I ../../include

libs=../../lib/$(mcu).c
app=echo

install: $(app)
	$(BSL) -e -p $(app).hex 
	$(BSL) -P $(app).hex -r
all: $(app).hex
$(app): $(app).c $(libs)
$(app).hex: $(app)
	msp430-objcopy -O ihex $(app) $(app).hex
erase:
	$(BSL) -e 
clean:
	rm -f $(app)
