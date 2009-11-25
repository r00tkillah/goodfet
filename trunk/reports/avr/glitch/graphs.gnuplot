# Generates graphs about glitching an Atmel AVR


#Stability graph.
set term post eps
set output 'stability.eps'
set xlabel "Voltage"
set ylabel "P[identify]"
set title "Atmel AVR Stability"
plot 'stability.txt'
