
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
	rm -rf target/*/build target/*/status

distclean:
	rm -rf src target
