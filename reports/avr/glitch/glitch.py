#!/usr/bin/env python

import sys,binascii,time,random;

sys.path.append('../../../trunk/client/')

from GoodFETAVR import GoodFETAVR;
from intelhex import IntelHex16bit, IntelHex;

import sqlite3;

#Learning phase
trials=1;
lock=0;  #1 locks, 0 unlocked
vstart=0;
vstop=1000;  #Smaller range sometimes helps.
vstep=1;
tstart=0;
tstop=-1; #<0 defaults to full range
tstep=0x1; #Must be 1



#Exploiting phase





#Database connection and tables.
db=sqlite3.connect("glitch.db");
db.execute("create table if not exists glitches(time,vcc,gnd,trials,glitchcount,count,lock)");

#Initialize FET and set baud rate
client=GoodFETAVR();
client.serInit()

print "-- GoodFET Unlock test."
print "-- Count of reads with voltage glitch."

if tstop<0:
    tstop=client.glitchstarttime();  #Really long; only use for initial investigation.
    print "-- Start takes %04i cycles." % tstop;

client.start();
client.erase();

secret=0x69;

#Erase chip for baseline.
while(client.eeprompeek(0)!=secret):
    print "-- Setting secret";
    client.start();
    
    #Flash the secret to the first two bytes of CODE memory.
    client.erase();
    client.eeprompoke(0,secret);
    client.eeprompoke(1,secret);
    
    print "-- readback %02x" % client.eeprompeek(0);
    sys.stdout.flush()

#Lock chip to unlock it later.
if lock>0:
    client.lock();

#FFF is full voltage

voltages=range(vstart,vstop,vstep);
times=range(tstart,tstop,tstep);

#times=[61];


#Self tests
print "--"
print "--"
print "-- %i trials/point, %i voltage skip" % (trials, vstep);
print "-- DAC Range %04i to %04i" % (vstart, vstop);
print "-- Time Range %04i to %04i" % (tstart, tstop);
print "-- Generated by GoodFET, http://goodfet.sf.net/"
print "-- %i points" % ((tstop-tstart)*(tstop-tstart)*trials/vstep)
print "-- Secret %02x" % secret;

sys.stdout.flush()

gnd=0;     #TODO, glitch GND.
vcc=0xfff;



random.shuffle(voltages);
random.shuffle(times);

commitcount=0;

#for time in times:
for vcc in voltages:
    #for vcc in voltages:
    for time in times:
        client.glitchRate(time);
        client.glitchVoltages(gnd, vcc);  #drop voltage target
        gcount=0;
        scount=0;
        print "-- (%i,%i)" % (time,vcc);
        sys.stdout.flush();
        for i in range(0,trials):
            commitcount+=1;
            client.glitchstart();
            
            #Try to read *0, which is secret if read works.
            a=client.eeprompeek(0x0);
            if lock>0: #locked
                if(a!=0 and a!=0xFF and a!=secret):
                    gcount+=1;
                if(a==secret):
                    print "-- %04x: %02x HELL YEAH! " % (time, a);
                    scount+=1;
            else: #unlocked
                if(a!=secret):
                    gcount+=1;
                if(a==secret):
                    scount+=1;
        print "values (%i,%i,%i,%i,%i);" % (
            time,vcc,gnd,gcount,scount);
        db.execute("insert into glitches(time,vcc,gnd,trials,glitchcount,count,lock)"
                   "values (%i,%i,%i,%i,%i,%i,%i);" % (
                time,vcc,gnd,trials,gcount,scount,lock));
        if commitcount>50:
            db.commit();
            commitcount=0;
    sys.stdout.flush()