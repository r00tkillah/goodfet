#TODO msp430x2
TARGETS=monitor cc 
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
nodiff: all
	svn diff $(TARGETS) | grep -v Index
