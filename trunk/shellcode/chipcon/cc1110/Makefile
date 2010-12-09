# These targets are compiled to execute at the beginning of RAM.
# Each should conclude with HALT (0xA5).

CC=sdcc --code-loc 0xF000 
objs=crystal.ihx

all: $(objs)

%.ihx : %.c
	$(CC) $<
clean:
	rm -f *.ihx *.rel *.hex *.sym *.asm *.lst *.lnk *.map *.mem *.rst *.adb
