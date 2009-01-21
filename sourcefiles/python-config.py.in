#! @PYTHON_FOR_BUILD@

import optparse
import sys

sys.version = '@PYTHON_VERSION@'

p = optparse.OptionParser ()
p.description = 'Python compile time configuration'

p.add_option ('', '--ldflags',
              default='',
              dest="ldflags",
              action="store_true",
              help="show ldflags")

p.add_option ('', '--libs',
              default='',
              dest="ldflags",
              action="store_true",
              help="show ldflags")

p.add_option ('', '--cflags',
              default=None,
              action="store_true",
              dest="cflags",
              help="show cflags")

p.add_option ('', '--includes',
              default=None,
              action="store_true",
              dest="cflags",
              help="show cflags")

p.add_option ('', '--verbose',
              action="store_true",
              default=False,
              dest="verbose",
              help="be verbose")

p.add_option ('', '--prefix',
              default=None,
              dest="prefix",
              help="set prefix")

(options, args) = p.parse_args ()

from distutils import sysconfig

sysconfig.PREFIX = '@PREFIX@'
sysconfig.EXEC_PREFIX = '@PREFIX@'

if options.prefix:
    sysconfig.EXEC_PREFIX = options.prefix
    sysconfig.PREFIX = options.prefix

if options.cflags:
    sys.stdout.write ('-I%s\n' % sysconfig.get_python_inc ())

if options.ldflags:
    extra = "@EXTRA_LDFLAGS@"
    if 0:
        mf = sysconfig.get_makefile_filename()
        d = sysconfig.parse_makefile (mf)
        if options.verbose:
            sys.stderr.write (mf + '\n')
        # Using flags from native python build is asking for trouble,
        # ie, arch or $$ORIGIN may break things.
        extra  = d['LDFLAGS']
        
    sys.stdout.write ('-L%s -L%s %s\n'
                      % (sysconfig.get_python_lib (),
                         sysconfig.PREFIX + '/lib/',
                         extra))

## -*-Python-*-
