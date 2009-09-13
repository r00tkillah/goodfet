#Generates distribution files for all targets.
#Testing is performed separately.

all:
	rm -rf dist
	mkdir dist
	echo "Options +Indexes" >dist/.htaccess
	cd ../trunk/firmware && mcu=msp430x1612 make clean all
	cp ../trunk/firmware/goodfet.hex dist/msp430x1612.hex
	cd ../trunk/firmware && mcu=msp430x2618 make clean all
	cp ../trunk/firmware/goodfet.hex dist/msp430x2618.hex
upload:
	rsync --exclude .svn -ave ssh dist travisutk,goodfet@web.sourceforge.net:htdocs/
