


all: graphs report 

report: glitch.sql
	sqlite3 -header -column glitch.sql "select time,sum(count) from glitches where count>0 group by time" | tee report/timecount.txt
graphs:
	gnuplot <graphs.gnuplot
follow:
	tail -f glitch.txt
run:
	./eeprom_locked.py | tee -a glitch.txt | sqlite3 glitch.sql
DOCS: stability.txt
	#Docs are ready.

clean:
	#Clean it yourself.
	#This data takes some time to generate.

