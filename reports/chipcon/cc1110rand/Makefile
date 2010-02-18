libs = rnd_rssi.rel
CC=sdcc
CFLAGS=--no-pack-iram


all: randtest.hex

%.rel : %.c
	$(CC) $(CFLAGS) -c $<

randtest.hex: randtest.rel $(libs)
	sdcc randtest.rel $(libs)
	packihx <randtest.ihx >randtest.hex

install: randtest.hex
	goodfet.cc erase
	goodfet.cc flash randtest.hex
verify: randtest.hex
	goodfet.cc verify randtest.hex
clean:
	rm -f *.hex *.ihx *.rel
