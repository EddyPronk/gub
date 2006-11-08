#! /usr/bin/python

def gcc_machine ():
        import os
        machine = os.popen ('gcc -dumpmachine 2>/dev/null').read ().strip ()
        lst = machine.split ('-')
        cpu = lst[0]
        if cpu in ('i386', 'i468', 'i586', 'i686'):
            cpu = 'x86'
        elif cpu == 'x86_64':
            cpu = '64'
        for os in lst[1:]:
            if os in ('linux', 'freebsd', 'darwin', 'cygwin'):
                return '%(os)s-%(cpu)s' % locals ()
        raise 'UnknownOs'

def main ():
    try:
        print gcc_machine ()
    except:
        # On failure print empty line for use in makefile's $(shell ).
        print

if __name__ == '__main__':
    main ()
