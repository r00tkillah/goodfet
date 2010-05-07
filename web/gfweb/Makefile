NANOC:=nanoc2

compile: 
	$(NANOC) compile
upload: compile
	rsync --exclude .svn -ave ssh output/* travisutk,goodfet@web.sourceforge.net:htdocs/
	rsync --exclude .svn -ave ssh ../../branches/*.zip travisutk,goodfet@web.sourceforge.net:htdocs/releases/
auto:
	$(NANOC) autocompile
