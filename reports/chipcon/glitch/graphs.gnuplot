# Generates graphs about glitching an Atmel AVR


#Stability graph.
set datafile separator "|"




set title "Chipcon CC1110 Glitching Metrics"
set term png
set output 'report/timevcc.png'
set xlabel "Time (16MHz Cycles)"
set ylabel "Voltage (DAC12)"
plot "< sqlite3 glitch.db 'select time,vcc,glitchcount from glitches where glitchcount>0;'" \
title "Errors", \
"< sqlite3 glitch.db 'select time,vcc,count from glitches where count>0;'" \
title "Success"
set term postscript
set output 'report/timevcc.eps'
replot


set title "Chipcon CC1110 Glitching Region"
set term png
set output 'report/region.png'
set xlabel "Time (16MHz Cycles)"
set ylabel "VCC"
plot "< sqlite3 glitch.db 'select time,vcc from glitches where count<80 order by time asc;'"  \
title "Out of Range", \
 "< sqlite3 glitch.db 'select time,vcc from glitches where count<98 and count>80  order by time asc;'"  \
title "Minimal read"
set term postscript
set output 'report/region.eps'
replot

set title "Chipcon CC1110 Glitching Metrics"
set term png
set output 'report/timecount.png'
set xlabel "Time (16MHz Cycles)"
set ylabel "Count"
plot "< sqlite3 glitch.db 'select time,glitchcount from glitches where glitchcount>0;'" \
title "Errors", \
"< sqlite3 glitch.db 'select time,count from glitches where count>0;'" \
title "Success"
set term postscript
set output 'report/timecount.eps'
replot


set title "Chipcon CC1110 Glitching Metrics"
set term png
set output 'report/vcccount.png'
set xlabel "VCC (DAC12)"
set ylabel "Count"
plot "< sqlite3 glitch.db 'select vcc,glitchcount from glitches where glitchcount>0;'" \
title "Errors", \
"< sqlite3 glitch.db 'select vcc,count from glitches where count>0;'" \
title "Success"
set term postscript
set output 'report/vcccount.eps'
replot

set title "Chipcon CC1110 Glitching Metrics"
set term png
set output 'report/3d.png'
set xlabel "Time"
set ylabel "VCC (DAC12)"
set zlabel "Count"
splot "< sqlite3 glitch.db 'select time,vcc,glitchcount from glitches where glitchcount>0;'" \
title "Errors", \
"< sqlite3 glitch.db 'select time,vcc,count from glitches where count>0 and count<100;'" \
title "Success"
set term postscript
set output 'report/3d.eps'
replot




# select time,vcc,1.0*count/glitchcount from glitches;
# select time,vcc,1.0*count/glitchcount as signoise, count, glitchcount from glitches order by signoise desc limit 10;
