# Generates graphs about glitching an Atmel AVR


#Stability graph.
set datafile separator "|"


set title "Atmel ATTiny45 Glitching Points"
set term png
set output 'report/timevcc.png'
set xlabel "Time (16MHz Cycles)"
set ylabel "Voltage (DAC12)"
plot "< sqlite3 glitch.db 'select time,vcc,glitchcount from glitches where count=0;'" with dots \
title "Scanned", \
"< sqlite3 glitch.db 'select time,vcc,count from glitches where count>0;'" with dots \
title "Success"
set term postscript
set output 'report/timevcc.eps'
replot



set title "Atmel ATTiny45 Glitching Metrics"
set term png
set output 'report/timecount.png'
set xlabel "Time (16MHz Cycles)"
set ylabel "Count"
plot "< sqlite3 glitch.db 'select time,glitchcount from glitches where count=0;'" \
title "Errors", \
"< sqlite3 glitch.db 'select time,count from glitches where count>0;'" \
title "Success"
set term postscript
set output 'report/timecount.eps'
replot


set title "Atmel ATTiny45 Glitching Metrics"
set term png
set output 'report/vcccount.png'
set xlabel "VCC (DAC12)"
set ylabel "Count"
plot "< sqlite3 glitch.db 'select vcc,glitchcount from glitches where count=0;'" \
title "Errors", \
"< sqlite3 glitch.db 'select vcc,count from glitches where count>0;'" \
title "Success"
set term postscript
set output 'report/vcccount.eps'
replot

set title "Atmel ATTiny45 Glitching Metrics"
set term png
set output 'report/3d.png'
set xlabel "Time"
set ylabel "VCC (DAC12)"
set zlabel "Count"
splot "< sqlite3 glitch.db 'select time,vcc,glitchcount from glitches where count=0;'" \
title "Errors", \
"< sqlite3 glitch.db 'select time,vcc,count from glitches where count>0 and count<100;'" \
title "Success"
set term postscript
set output 'report/3d.eps'
replot




# select time,vcc,1.0*count/glitchcount from glitches;
# select time,vcc,1.0*count/glitchcount as signoise, count, glitchcount from glitches order by signoise desc limit 10;
