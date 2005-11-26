
MINGW_RUNTIME_DIR = /usr
export MINGW_RUNTIME_DIR

default: all

all:
	python driver.py mac mingw

mac:
	python driver.py mac

mingw:
	python driver.py mingw

realclean:
	rm -rf src target

distclean: realclean
	echo NOT rm -rf downloads
