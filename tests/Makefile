
#Missing tagets: msp430x2
TARGETS=monitor cc

all: $(TARGETS)
clean:
	rm -f $(TARGETS) *~

monitor: monitor.zsh
	GOODFET=/dev/ttyUSB0 ./monitor.zsh >monitor
cc: cc.zsh
	GOODFET=/dev/ttyUSB1 ./cc.zsh >cc
msp430x2: msp430x2.zsh
	./msp430x2.zsh >msp430x2
