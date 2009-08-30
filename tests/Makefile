TARGETS=monitor cc
GOODFET=/dev/ttyUSB0

all: $(TARGETS)
clean:
	rm -f $(TARGETS)

monitor: monitor.zsh
	./monitor.zsh >monitor
cc: cc.zsh
	./cc.zsh >cc
