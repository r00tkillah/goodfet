


all: graphs rep

rep: glitch.sql
	sqlite3 -header -column glitch.sql "select time,sum(count),1.0*sum(count)/sum(glitchcount)  from glitches where count>0 group by time" | tee report/timecount.txt
	sqlite3 -header -column glitch.sql "select time,vcc,1.0*count/glitchcount as signoise, count, glitchcount from glitches order by signoise desc limit 10;" | tee report/topten.txt
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

