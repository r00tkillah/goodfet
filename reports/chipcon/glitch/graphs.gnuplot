# Generates graphs about glitching an Atmel AVR


#Stability graph.
set datafile separator "|"




set title "Chipcon CC1110 Glitching Metrics"
set term png
set output 'report/timevcc.png'
set xlabel "Time (16MHz Cycles)"
set ylabel "Voltage (DAC12)"
plot "< sqlite3 glitch.sql 'select time,vcc,glitchcount from glitches where count=0;'" \
title "Errors", \
"< sqlite3 glitch.sql 'select time,vcc,count from glitches where count>0;'" \
title "HELL YES"
set term postscript
set output 'report/timevcc.eps'
replot

set title "Chipcon CC1110 Glitching Metrics"
set term png
set output 'report/timecount.png'
set xlabel "Time (16MHz Cycles)"
set ylabel "Count"
plot "< sqlite3 glitch.sql 'select time,glitchcount from glitches where count=0;'" \
title "Errors", \
"< sqlite3 glitch.sql 'select time,count from glitches where count>0;'" \
title "HELL YES"
set term postscript
set output 'report/timecount.eps'
replot

set title "Chipcon CC1110 Glitching Metrics"
set term png
set output 'report/vcccount.png'
set xlabel "VCC (DAC12)"
set ylabel "Count"
plot "< sqlite3 glitch.sql 'select vcc,glitchcount from glitches where count=0;'" \
title "Errors", \
"< sqlite3 glitch.sql 'select vcc,count from glitches where count>0;'" \
title "HELL YES"
set term postscript
set output 'report/vcccount.eps'
replot

set title "Chipcon CC1110 Glitching Metrics"
set term png
set output 'report/3d.png'
set xlabel "VCC (DAC12)"
set ylabel "Count"
splot "< sqlite3 glitch.sql 'select time,vcc,glitchcount from glitches where count=0;'" \
title "Errors", \
"< sqlite3 glitch.sql 'select time,vcc,count from glitches where count>0;'" \
title "HELL YES"
set term postscript
set output 'report/3d.eps'
replot




# select time,vcc,1.0*count/glitchcount from glitches;
# select time,vcc,1.0*count/glitchcount as signoise, count, glitchcount from glitches order by signoise desc limit 10;
