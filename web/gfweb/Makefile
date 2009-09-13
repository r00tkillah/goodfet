compile: 
	nanoc compile
upload: compile
	rsync --exclude .svn -ave ssh output/* travisutk,goodfet@web.sourceforge.net:htdocs/
auto:
	nanoc autocompile
