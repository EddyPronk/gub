import os

def sanatize_cpu (cpu):
    if cpu in ('i386', 'i486', 'i586', 'i686'):
        cpu = 'x86'
    elif cpu == 'x86_64':
        cpu = '64'
    return cpu

def gcc_machine ():
    machine = os.popen ('gcc -dumpmachine 2>/dev/null').read ().strip ()
    lst = machine.split ('-')
    cpu = sanatize_cpu (lst[0])
    for os_name in lst[1:]:
        if os_name in ('linux', 'freebsd', 'darwin', 'cygwin'):
            return '%(os_name)s-%(cpu)s' % locals ()
    raise 'UnknownOs'

def uname_machine ():
    machine = os.popen ('uname -ms 2>/dev/null').read ().strip ()
    os_name, cpu = machine.split (' ')
    cpu = sanatize_cpu (cpu)
    os_name = os_name.lower ()
    if os_name in ('linux', 'freebsd', 'darwin', 'cygwin'):
        return '%(os_name)s-%(cpu)s' % locals ()
    raise 'UnknownOs'

def machine ():
    try:
        return gcc_machine ()
    except:
        return uname_machine ()
    raise 'UnknownOs'
