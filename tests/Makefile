#TODO msp430x2
TARGETS=cc spiflash
GOODFET=/dev/ttyUSB0

all: 
	make clean
	make flash
	make $(TARGETS)
clean:
	rm -f $(TARGETS) *~
flash:
	./flashall.zsh
monitor: monitor.zsh
	GOODFET=/dev/ttyUSB0 ./monitor.zsh >monitor
cc: cc.zsh
	GOODFET=/dev/ttyUSB1 ./cc.zsh >cc
msp430x2: msp430x2.zsh
	./msp430x2.zsh >msp430x2
spiflash:
	GOODFET=/dev/ttyUSB0 ../trunk/client/goodfet.spiflash test >spiflash
nodiff: all
	#If this fails, it's because a test result differs with the one in svn.
	if (svn diff $(TARGETS) | grep Index); then false; fi

