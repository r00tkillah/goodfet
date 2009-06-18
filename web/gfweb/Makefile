compile: 
	nanoc compile
upload: compile
	rsync --exclude .svn --delete -ave ssh output/* travisutk,goodfet@web.sourceforge.net:htdocs/
