# Generates graphs about glitching an Atmel AVR


#Stability graph.
set datafile separator "|"
set term png
set output 'eeprom_locked.png'
set xlabel "Time"
set ylabel "Voltage"
set title "ATTiny45"

plot "< sqlite3 glitch.sql 'select time,vcc,count from glitches where count>0;'" \
title "Recover", \
"< sqlite3 glitch.sql 'select time,vcc,count from glitches where count=0;'" \
title "Error"

