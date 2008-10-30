from gub.specs.cross import binutils
from gub import misc

class Binutils__freebsd (binutils.Binutils):
    source = 'ftp://ftp.gnu.org/pub/gnu/binutils/binutils-2.18.tar.bz2'
    patches = binutils.Binutils.patches
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        return (binutils.Binutils.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(toolchain_prefix)s
'''))
