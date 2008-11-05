import os

def read_pipe (command):
    return os.popen ('%(command)s 2>/dev/null' % locals ()).read ().strip ()

def sanatize_cpu (cpu):
    if cpu in ('i386', 'i486', 'i586', 'i686'):
        cpu = 'x86'
    elif cpu == 'x86_64':
        cpu = '64'
    return cpu

def plain_gcc_machine ():
    return read_pipe ('gcc -dumpmachine')

def gcc_machine ():
    machine = plain_gcc_machine ()
    lst = machine.split ('-')
    cpu = sanatize_cpu (lst[0])
    for os_name in lst[1:]:
        if os_name in ('linux', 'freebsd', 'darwin', 'cygwin'):
            return '%(os_name)s-%(cpu)s' % locals ()
    raise 'UnknownOs'

def plain_uname_machine ():
    return '-'.join ([read_pipe ('uname -m'), read_pipe ('uname -s')])

def uname_machine ():
    machine = plain_uname_machine ()
    cpu, os_name = machine.split ('-')
    cpu = sanatize_cpu (cpu)
    os_name = os_name.lower ()
    if os_name in ('linux', 'freebsd', 'darwin', 'cygwin'):
        return '%(os_name)s-%(cpu)s' % locals ()
    raise 'UnknownOs'

def plain_machine ():
    m = plain_gcc_machine ()
    if not m:
        m = plain_uname_machine ()
    return m

def machine ():
    try:
        return gcc_machine ()
    except:
        return uname_machine ()
    raise 'UnknownOs'
