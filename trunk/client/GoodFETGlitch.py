#!/usr/bin/env python
# GoodFET Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, time, string, cStringIO, struct, glob, serial, os, random;
import sqlite3;

from GoodFET import *;


# YScale should be to "select max(vcc) from glitches where count=0;"

script_timevcc="""
plot "< sqlite3 glitch.db 'select time,vcc,glitchcount from glitches where count=0;'" \
with dots \
title "Scanned", \
"< sqlite3 glitch.db 'select time,vcc,count from glitches where count>0;'" \
with dots \
title "Success", \
"< sqlite3 glitch.db 'select time,vcc,count from glitches where count>0 and lock>0;'" \
with dots \
title "Exploited"
""";

script_timevccrange="""
plot "< sqlite3 glitch.db 'select time,vcc,glitchcount from glitches where count=0;'" \
with dots \
title "Scanned", \
"< sqlite3 glitch.db 'select time,vcc,count from glitches where count>0;'" \
with dots \
title "Success", \
"< sqlite3 glitch.db 'select time,max(vcc),count from glitches where count=0 group by time ;'" with lines title "Max", \
"< sqlite3 glitch.db 'select time,min(vcc),count from glitches where count>0 group by time ;'" with lines title "Min"
""";

class GoodFETGlitch(GoodFET):
    
    def __init__(self, *args, **kargs):
        print "Initializing GoodFET Glitcher."
        #Database connection w/ 30 second timeout.
        self.db=sqlite3.connect("glitch.db",30000);
        self.db.execute("create table if not exists glitches(time,vcc,gnd,trials,glitchcount,count,lock)");
        self.db.execute("create index if not exists glitchvcc on glitches(vcc);");
        self.db.execute("create index if not exists glitchtime on glitches(time);");
        self.client=0;
    def setup(self,arch="avr"):
        self.client=getClient(arch);
    def graphx11(self):
        try:
            import Gnuplot, Gnuplot.PlotItems, Gnuplot.funcutils
        except ImportError:
            print "gnuplot-py is missing.  Can't graph."
            return;
        g = Gnuplot.Gnuplot(debug=1);
        g.clear();
        
        g.title('Glitch Training Set');
        g.xlabel('Time (16MHz)');
        g.ylabel('VCC (DAC12)');
        
        g('set datafile separator "|"');
        
        g(script_timevcc);
        print "^C to exit.";
        while 1==1:
            time.sleep(30);
        #    g('replot');

        
    def graph(self):
        #try:
        import Gnuplot, Gnuplot.PlotItems, Gnuplot.funcutils
        #except ImportError:
        #    print "py-gnuplot or py-numpy is missing.  Can't graph."
        #    return;
        g = Gnuplot.Gnuplot(debug=1);
        
        g('\nset term png');
        g.title('Glitch Training Set');
        g.xlabel('Time (16MHz)');
        g.ylabel('VCC (DAC12)');
        
        g('set datafile separator "|"');
        g('set term png');
        g('set output "timevcc.png"');
        g(script_timevcc);
        
    def learn(self):
        #Learning phase
        trials=1;
        lock=0;  #1 locks, 0 unlocked
        vstart=0;
        vstop=0xfff;  #Could be as high as 0xFFF
        vstep=1;
        tstart=0;
        tstop=-1; #<0 defaults to full range
        tstep=0x1; #Must be 1
        self.scan(lock,trials,vstart,vstop,tstart,tstop);

    def scan(self,lock,trials=1,vstart=0,vstop=0xfff,tstart=0,tstop=-1):
        client=self.client;
        self.lock=lock;
        client.serInit();
        if tstop<0:
            tstop=client.glitchstarttime();  #Really long; only use for initial investigation.
            print "-- Start takes %04i cycles." % tstop;
        client.start();
        client.erase();
        
        self.secret=0x69;

        while(client.eeprompeek(0)!=self.secret):
            print "-- Setting secret";
            client.start();
            
            #Flash the secret to the first two bytes of CODE memory.
            client.erase();
            client.eeprompoke(0,self.secret);
            client.eeprompoke(1,self.secret);
            sys.stdout.flush()

        #Lock chip to unlock it later.
        if lock>0:
            client.lock();
        voltages=range(vstart,vstop,1);
        times=range(tstart,tstop,1);
        
        gnd=0;     #TODO, glitch GND.
        vcc=0xfff;
        random.shuffle(voltages);
        #random.shuffle(times);
        
        for vcc in voltages:
            if not self.vccexplored(vcc):
                print "Exploring vcc=%i" % vcc;
                sys.stdout.flush();
                for time in times:
                    self.scanat(trials,vcc,gnd,time)
                    sys.stdout.flush()
                self.db.commit();
            else:
                print "Voltage %i already explored." % vcc;
                sys.stdout.flush();
    def vccexplored(self,vcc):
        c=self.db.cursor();
        c.execute("select vcc from glitches where vcc=? limit 1;",[vcc]);
        rows=c.fetchall();
        for a in rows:
            return True;
        return False; 
    def scanat(self,trials,vcc,gnd,time):
        client=self.client;
        db=self.db;
        client.glitchRate(time);
        client.glitchVoltages(gnd, vcc);  #drop voltage target
        gcount=0;
        scount=0;
        #print "-- (%5i,%5i)" % (time,vcc);
        #sys.stdout.flush();
        for i in range(0,trials):
            client.glitchstart();
            
            #Try to read *0, which is secret if read works.
            a=client.eeprompeek(0x0);
            if self.lock>0: #locked
                if(a!=0 and a!=0xFF and a!=self.secret):
                    gcount+=1;
                if(a==self.secret):
                    print "-- %04x: %02x HELL YEAH! " % (time, a);
                    scount+=1;
            else: #unlocked
                if(a!=self.secret):
                    gcount+=1;
                if(a==self.secret):
                    scount+=1;
        #print "values (%i,%i,%i,%i,%i);" % (
        #    time,vcc,gnd,gcount,scount);
        self.db.execute("insert into glitches(time,vcc,gnd,trials,glitchcount,count,lock)"
                   "values (%i,%i,%i,%i,%i,%i,%i);" % (
                time,vcc,gnd,trials,gcount,scount,self.lock));
