#!/usr/bin/env python

import sys,binascii,time,random;

sys.path.append('../../../trunk/client/')

from GoodFETAVR import GoodFETAVR;
from intelhex import IntelHex16bit, IntelHex;

#Initialize FET and set baud rate
client=GoodFETAVR();
client.serInit()

#Connect to target
client.start();

#1,000 takes an hour
trials=5; #10,000 is smooth

print "# GoodFET EEPROM Unlock test."
print "# Count of reads with voltage glitch."

client.glitchVoltages(0, 0xFFF);  #Jump voltage.

client.start();
client.erase();

secret=0x0F
#Erase chip for baseline.
while(client.eeprompeek(0)!=secret):
    #print "Setting secret";
    client.start();
    client.erase();
    client.eeprompoke(0,secret);
    client.eeprompoke(1,secret);
    

#Lock chip to unlock it later.
client.setlockbits(0xFC);

#0xfff is full voltage
#highv=0x900; #Works, but clock errors are common.
highv=0xfff; #For dropping and not returning.
#highv=0xA00;

vstart=0x0;
vstop=0x900;  #Smaller range sometimes helps.
skip=1;

#Time Range, wide search.
tstart=0x400;
tstop=client.glitchstarttime();  #Really long; only use for initial investigation.
#tstop=0x100;
print "# AVRStart takes %04x cycles." % tstop;
tstep=0x1; #Must be 1




#Restrict range to glitch at 39 {01e7, 01c1, 01da, 01d8, 01c4, 01d5}
#tstart=0x0039
#tstop=0x0100
#vstart=0x1c0
#vstop=0x1f0


vstart=0xFF0;
vstop=0xFFF;

#Self tests
print "#"


print "#"
print "# %i trials/point, %i steps/point" % (trials, skip);
print "# DAC Range %04x to %04x" % (vstart, vstop);
print "# Time Range %04x to %04x" % (tstart, tstop);
print "# Generated by GoodFET, http://goodfet.sf.net/"
print "# %i points" % ((tstop-tstart)*(tstop-tstart)*trials/skip)

sys.stdout.flush()

voltages=range(vstart,vstop,skip);
times=range(tstart,tstop,tstep);

random.shuffle(voltages);
#random.shuffle(times);

for va in voltages:
#for time in times:
    print "# Row %04x" % va;
    #print "# Column %04x" % time;
    for time in times:
    #for va in voltages:
        client.glitchVoltages(0, va);  #drop voltage target
        client.glitchRate(time);
        gcount=0;
        scount=0;
        for i in range(0,trials):
            #Old start
            client.start();
            #Glitching AVR/Start
            #client.glitchstart();
            
            
            #Try to read *0, which is 0xDE if read works.
            #a=client.eeprompeek(0)
            a=client.lockbits();
            
            b=client.eeprompeek(0);
            c=client.eeprompeek(1);
            
            if(a!=0xFC):
                print "# %04x: %02x %02x %02x" % (time, a,b,c);
                gcount+=1;
            if(b==secret):
                print "# HELL YEAH! %04x: %02x %02x %02x" % (time, a,b,c);
                sys.stdout.flush()
                scount+=1;
            
        if(gcount>0 or scount>0):
            print "#Glitched from %04x at %04x" % (va,time);
            print "%d, %f, %d, %d, %d" % (
                va, va*(3.3/4096.0),time,
                gcount, scount);
        sys.stdout.flush()
