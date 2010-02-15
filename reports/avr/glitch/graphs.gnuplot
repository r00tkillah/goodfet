# Generates graphs about glitching an Atmel AVR


#Stability graph.
set datafile separator "|"
set term png

set title "ATTiny45"

set output 'report/timevcc.png'
set xlabel "Time"
set ylabel "Voltage"
plot "< sqlite3 glitch.sql 'select time,vcc,count from glitches where count>0;'" \
title "Recover", \
"< sqlite3 glitch.sql 'select time,vcc,count from glitches where count=0;'" \
title "Error"

set output 'report/timecount.png'
set xlabel "Time"
set ylabel "Count"
plot "< sqlite3 glitch.sql 'select time,sum(count) from glitches where count>0 group by time;'" \
with lines \
title "Glitches"
