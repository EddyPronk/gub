#! /usr/bin/python

class Gcc_machine:
    _platforms = {
        'i386-redhat-linux': 'linux-x86',
        'i486-linux-gnu': 'linux-x86',
        'i686-pc-cygwin': 'cygwin',
        'x86_64-linux-gnu': 'linux-64',
        }
    def __init__ (self):
        import os
        machine = os.popen ('gcc -dumpmachine 2>/dev/null').read ().strip ()
        if self._platforms.has_key (machine):
            self._platform = self._platforms[machine]
        else:
            self._platform = self.guess_platform (machine.split ('-'))
    def guess_platform (self, machine):
        cpu = machine[0]
        if cpu in ('i386', 'i468', 'i586', 'i686'):
            cpu = 'x86'
        elif cpu == 'x86_64':
            cpu = '64'
        for os in machine[1:]:
            if os in ('linux', 'freebsd', 'darwin', 'cygwin'):
                return '%(cpu)s-%(os)s' % locals ()
    def __str__ (self):
        return self._platform

def main ():
    try:
        print Gcc_machine ()
    except:
        # On failure print empty line for use in makefile's $(shell ).
        print

if __name__ == '__main__':
    main ()
