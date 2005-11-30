
default: all

all:
	python driver.py linux mac mingw

linux:
	python driver.py linux

mac:
	python driver.py mac

mingw:
	python driver.py -V mingw

realclean:
	rm -rf src target

distclean: realclean
	echo NOT rm -rf downloads
