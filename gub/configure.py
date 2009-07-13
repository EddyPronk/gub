import os
import re
import sys
import string
#
from gub.syntax import printf
from gub import misc

dre = re.compile ('\n(200[0-9]{5})')
vre = re.compile ('.*?\n[^-.0-9]*([0-9][0-9]*\.[0-9]([.0-9]*[0-9])*)', re.DOTALL)

# FIXME: hasty reworkings of ancient and ugly SConscript.configure code

def get_version (program):
    command = '(pkg-config --modversion %(program)s || %(program)s --version || %(program)s -V) 2>&1' % vars ()
    output = misc.read_pipe (command)
    splits = re.sub ('^|\s', '\n', output)
    date_hack = re.sub (dre, '\n0.0.\\1', splits)
    m = re.match (vre, date_hack)
    v = m.group (1)
    if v[-1] == '\n':
        v = v[:-1]
    return v.split ('.')

def test_version (lst, full_name, minimal, description='', package=None, logger=sys.stderr):
    if not package:
        package = full_name
    if not description:
        description = package
    program = os.path.basename (full_name)
    logger.write ('Checking %(program)s version... ' % locals ())
    actual = get_version (program)
    if not actual:
        logger.write ('not found\n')
        lst.append ((description, package, minimal, program,
                 'not installed'))
        return 0
    logger.write ('.'.join (actual) + '\n')
    if (map (string.atoi, actual)
        < map (string.atoi, minimal.split ('.'))):
        entry = (description, package, minimal, program, '.'.join (actual))
        if not entry in lst:
            lst.append (entry)
        return 0
    return 1

def test_program (lst, program, minimal, description='', package=None, env={}, logger=sys.stderr):
    if not package:
        package = program
    if not description:
        description = package
    key = (program.upper ()
           .replace ('+-', 'X_'))
    logger.write ('Checking for %(program)s ... ' % locals ())
    if key in list (env.keys ()):
        f = env[key]
        logger.write ('(cached) ')
    else:
        f = misc.path_find (os.environ['PATH'], program)
        env[key] = f
    if not f:
        logger.write ('not found\n')
        entry = (description, package, minimal, program, 'not installed')
        if not entry in lst:
            lst.append (entry)
        return 0
    logger.write (f + '\n')
    if minimal:
        return test_version (lst, program, minimal, description, package, logger)
    return 1

optional = []
required = []
def test_required (logger):
    if required:
        logger.write ('\n')
        printf ('********************************')
        printf ('Please install required packages')
        for i in required:
            printf ('%s:	%s-%s or newer (found: %s %s)\n' % i)
        sys.exit (1)

def test ():
    global required
    test_program (required, 'gcc', '3.4', 'GNU C compiler; 4.x strongly recommended', 'gcc')
    test_program (required, 'xc++', '2.2', 'X C++ compiler; discouraged')
    test_program (required, 'g++', None, 'GNU C++ compiler; 4.x is strongly recommended', 'g++')
    test_program (required, 'make', '3.78', 'GNU make', 'make')
    test_required (sys.stderr)
                  
if __name__ =='__main__':
    test ()
