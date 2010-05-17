

link:
	rm -f /usr/local/bin/goodfet.* /usr/local/bin/goodfet
	rm -rf *~
	mkdir -p /usr/local/bin
	ln -s `pwd`/goodfet `pwd`/goodfet.* /usr/local/bin/
install:
	echo "Try 'make link' instead."

py2exepub:
#publish the windows build.
	rsync --exclude .svn -ave ssh tmp/goodfet.zip travisutk,goodfet@web.sourceforge.net:htdocs/dist/gfwin.zip
py2exe:
#Run this from Win32 with Python, py2exe, py-serial, and GNU utils.
#MSP430 Client
	sed s/PYTHONCONSOLE/goodfet.msp430/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gf430.exe
#Monitor
	sed s/PYTHONCONSOLE/goodfet.monitor/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfmon.exe
#BSL
	sed s/PYTHONCONSOLE/goodfet.bsl/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfbsl.exe
#BSL
	sed s/PYTHONCONSOLE/goodfet.bsl/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfbsl.exe
#AVR
	sed s/PYTHONCONSOLE/goodfet.avr/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfavr.exe
#Chipcon
	sed s/PYTHONCONSOLE/goodfet.cc/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfcc.exe
#SPI Flash
	sed s/PYTHONCONSOLE/goodfet.spiflash/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfspi.exe
#Goodfet.  This must be last.
	sed s/PYTHONCONSOLE/goodfet/ <p2e.txt >setup.py
	python setup.py py2exe
#	mv dist/goodfet.exe dist/goodfet.exe
#Now package it all.
	rm -rf tmp
	mkdir -p tmp/goodfet
	mv dist/* tmp/goodfet/
	cd tmp && zip -r goodfet.zip goodfet

