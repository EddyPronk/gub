from gub import cross
from gub import mirrors

class Binutils (cross.Binutils):
    def __init__ (self, settings):
        cross.Binutils.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnu, version='2.16.1', format='bz2')

# FIXME: setting binutil's tooldir and/or gcc's gcc_tooldir may fix
# -luser32 (ie -L .../w32api/) problem without having to set LDFLAGS.
class Binutils__cygwin (Binutils):
    def __init__ (self, settings):
        Binutils.__init__ (self, settings)
        self.with (version='2.17', format='bz2', mirror=mirrors.gnu)
    def makeflags (self):
        from gub import misc
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def compile_command (self):
        return (cross.Binutils.compile_command (self)
                + self.makeflags ())
    def configure_command (self):
        return ( cross.Binutils.configure_command (self)
                 + ' --disable-werror ')

class Binutils__freebsd (Binutils):
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        from gub import misc
        return (cross.Binutils.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(tool_prefix)s
'''))
