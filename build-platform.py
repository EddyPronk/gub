#! /usr/bin/python

class Gcc_machine:
    _platforms = {
	'i686-pc-cygwin': 'cygwin',
	'x86_64-linux-gnu': 'linux-64',
	'i486-linux-gnu': 'linux-x86',
	}
    def __init__ (self):
	import os
	machine = os.popen ('gcc -dumpmachine 2>/dev/null').read ().strip ()
	self._platform = self._platforms[machine]
    def __str__ (self):
	return self._platform

def main ():
    try:
	print Gcc_machine ()
    except:
	print

if __name__ == '__main__':    
    main ()
