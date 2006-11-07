#! /usr/bin/python

platforms = {
    'i686-pc-cygwin': 'cygwin',
    'x86_64-linux-gnu': 'linux-64',
    'i486-linux-gnu': 'linux-x86',
    }

def main ():
    import os
    m = os.popen ('gcc -dumpmachine 2>/dev/null').read ()
    if m.endswith ('\n'):
	m = m[:-1]
    if m in platforms:
	print platforms[m]
    else:
	print ''

if __name__ == '__main__':    
    main ()
