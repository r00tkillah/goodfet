
hidapi:
	git clone -b release git://github.com/thequux/hidapi.git

hidapi-linux2-x86_64.so:
	make -C hidapi/linux EXTRA_CFLAGS=-m64 clean hidapi.so && mv hidapi/linux/hidapi.so $@

hidapi-linux2-x86_32.so:
	make -C hidapi/linux EXTRA_CFLAGS=-m32 clean hidapi.so && mv hidapi/linux/hidapi.so $@
