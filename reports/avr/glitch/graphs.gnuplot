# Generates graphs about glitching an Atmel AVR


#Stability graph.
set datafile separator "|"




set title "ATTiny45 Glitching Metrics"
set term png
set output 'report/timevcc.png'
set xlabel "Time (16MHz Cycles)"
set ylabel "Voltage"
plot "< sqlite3 glitch.sql 'select time,vcc,count,1.0*count/glitchcount as signoise from glitches where signoise>1;'" \
title "Good", \
"< sqlite3 glitch.sql 'select time,vcc,count,1.0*count/glitchcount as signoise from glitches where signoise<1 and signoise>0;'" \
title "Passable"
set term postscript
set output 'report/timevcc.eps'
replot


set title "ATTiny45 Glitching Metrics"
set term png
set output 'report/timecount.png'
set xlabel "Time (16MHz Cycles)"
set ylabel "Avg Signal/Noise"
plot "< sqlite3 glitch.sql 'select time,1.0*sum(count)/sum(glitchcount) as signoise from glitches where count>0 group by time;'" \
with lines \
title "Glitches"
set term postscript
set output 'report/timecount.eps'
replot

# select time,vcc,1.0*count/glitchcount from glitches;
# select time,vcc,1.0*count/glitchcount as signoise, count, glitchcount from glitches order by signoise desc limit 10;
