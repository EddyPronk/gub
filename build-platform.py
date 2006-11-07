#! /usr/bin/python
import re
import os
        
def platform ():
    _platforms = {
	'i686-pc-cygwin': 'cygwin',
	'x86_64-linux-gnu': 'linux-64',
	'i486-linux-gnu': 'linux-x86',
	}

    machine = os.popen ('gcc -dumpmachine 2>/dev/null').read ().strip ()
    
    try:
        return _platforms[machine]
    except KeyError:
        cpu = machine.split ('-')[0]
        op_sys = ''
        if re.search ('i[0-9]86', cpu):
            cpu = 'x86'
        elif re.search ('x86_64', cpu):
            cpu = '64'
            
        for a in ['linux', 'freebsd', 'darwin']:
            if a in machine:
                op_sys = a
                
        return '%s-%s' % (op_sys, cpu) 
    
def main ():

    ## fail silently, so usable in $(shell ) in makefile.
    try:
        print platform ()
    except:
        print 

if __name__ == '__main__':    
    main ()
