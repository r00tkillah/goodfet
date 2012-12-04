-include config.mk


all:
	board=facedancer11 make stl
	board=goodfet41 make stl
stl:
	openscad -o $(board)_bot.stl -D renderbot=1 -D rendertop=0 $(config) goodfetlib.scad
	openscad -o $(board)_top.stl -D renderbot=0 -D rendertop=1 $(config) goodfetlib.scad
clean:
	rm -f *.stl *~
