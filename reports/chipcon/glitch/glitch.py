#!/usr/bin/env python

import sys,binascii,time,random;

sys.path.append('../../../trunk/client/')

from GoodFETCC import GoodFETCC;
from intelhex import IntelHex16bit, IntelHex;

import sqlite3;

#Database connection and tables.
db=sqlite3.connect("glitch.db");
db.execute("create table if not exists glitches(time,vcc,gnd,trials,glitchcount,count)");

#Initialize FET and set baud rate
client=GoodFETCC();
client.serInit()

print "-- GoodFET EEPROM Unlock test."
print "-- Count of reads with voltage glitch."

client.start();
client.erase();

secret=0x69;

#Erase chip for baseline.
while(client.CCpeekcodebyte(0)!=secret):
    print "-- Setting secret";
    client.start();
    
    #Flash the secret to the first two bytes of CODE memory.
    client.CCeraseflashbuffer();
    client.CCpokedatabyte(0xF000,secret);
    client.CCpokedatabyte(0xF001,secret);
    client.CCflashpage(0);
    
    print "-- readback %02x" % client.CCpeekcodebyte(0);
    sys.stdout.flush()

#Lock chip to unlock it later.
#client.lock();

#FFF is full voltage

vstart=0;
vstop=900;  #Smaller range sometimes helps.
vstep=1;

#Time Range, wide search.
tstart=0;
tstop=client.glitchstarttime();  #Really long; only use for initial investigation.
#tstop=100; #By experiment, not sure where the other 80 cycles come from.
tstop=150;

print "-- Start takes %04i cycles." % tstop;
tstep=0x1; #Must be 1


voltages=range(vstart,vstop,vstep);
times=range(tstart,tstop,tstep);

#times=[61];
trials=1;

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

gnd=0xFFF;     #TODO, glitch GND.
vcc=0xfff;



random.shuffle(voltages);
#random.shuffle(times);

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
            #client.start();
            client.glitchstart();
            
            #Try to read *0, which is secret if read works.
            a=client.CCpeekcodebyte(0x0);
            #b=client.CCstatus();
            #c=client.CCpeekcodebyte(0x0);
            
            if(a!=0 and a!=0xFF and a!=secret):
                gcount+=1;
                #print "-- %04x: %02x %02x %02x" % (time, a,b,c);
            if(a==secret):
                print "-- %04x: %02x HELL YEAH! " % (time, a);
                scount+=1;
            
        print "values (%i,%i,%i,%i,%i);" % (
            time,vcc,gnd,gcount,scount);
        db.execute("insert into glitches(time,vcc,gnd,trials,glitchcount,count)"
                   "values (%i,%i,%i,%i,%i,%i);" % (
                time,vcc,gnd,trials,gcount,scount));
        db.commit();
    sys.stdout.flush()
