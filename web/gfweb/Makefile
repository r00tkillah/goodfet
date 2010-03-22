compile: 
	nanoc compile
upload: compile
	rsync --exclude .svn -ave ssh output/* travisutk,goodfet@web.sourceforge.net:htdocs/
	rsync --exclude .svn -ave ssh ../../branches/*.zip travisutk,goodfet@web.sourceforge.net:htdocs/releases/
auto:
	nanoc autocompile
