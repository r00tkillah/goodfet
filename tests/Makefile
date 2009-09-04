TARGETS=monitor cc spiflash


all: $(TARGETS)
clean:
	rm -f $(TARGETS) *~

monitor: monitor.zsh
	GOODFET=/dev/ttyUSB0 ./monitor.zsh >monitor
cc: cc.zsh
	GOODFET=/dev/ttyUSB1 ./cc.zsh >cc
spiflash: spiflash.zsh
	GOODFET=/dev/ttyUSB0 ./spiflash.zsh >spiflash
