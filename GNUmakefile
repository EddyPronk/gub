
default: all

all:
	python driver.py mac mingw

mac:
	python driver.py mac

mingw:
	python driver.py -V mingw

realclean:
	rm -rf src target

distclean: realclean
	echo NOT rm -rf downloads
