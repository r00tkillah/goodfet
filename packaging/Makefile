#Generates distribution files for all targets.
#Testing is performed separately.

gfpath?=.tmpbuild
fwpath=$(gfpath)/trunk/firmware
hwpath=$(gfpath)/trunk/hardware
clientpath=$(gfpath)/trunk/client
testpath=$(gfpath)/tests


all:
	rm -rf dist
	mkdir dist
	echo "Options +Indexes" >dist/.htaccess
	rm -rf $(gfpath)
	svn co https://goodfet.svn.sourceforge.net/svnroot/goodfet $(gfpath)
	#cd $(testpath) && make nodiff 
	cd $(fwpath) && mcu=msp430x1612 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/msp430x1612.hex >/dev/null
	cd $(fwpath) && mcu=msp430x2618 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/msp430x2618.hex >/dev/null
	cd $(fwpath) && mcu=msp430x2274 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/msp430x2274.hex >/dev/null
	cp $(clientpath)/*.py $(clientpath)/goodfet.* dist
	cp distreadme.txt dist/README.txt
	#cp $(hwpath)/*.sch $(hwpath)/*.brd dist/
	cd dist && zip goodfet.zip *
clean:
	rm -f *.hex *~ $(gfpath)
upload: all
	rsync --exclude .svn -ave ssh --delete dist travisutk,goodfet@web.sourceforge.net:htdocs/
