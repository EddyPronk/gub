#! /usr/bin/python

"""
    Copyright (c) 2005--2007
    Jan Nieuwenhuizen <janneke@gnu.org>
    Han-Wen Nienhuys <hanwen@xs4all.nl>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""


def gcc_machine ():
        import os
        machine = os.popen ('gcc -dumpmachine 2>/dev/null').read ().strip ()
        lst = machine.split ('-')
        cpu = lst[0]
        if cpu in ('i386', 'i486', 'i586', 'i686'):
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
