from gub.specs.cross import binutils as cross_binutils
from gub import misc

class Binutils__freebsd (cross_binutils.Binutils):
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        return (cross_binutils.Binutils.configure_command (self)
                + misc.join_lines ('''
--program-prefix=%(toolchain_prefix)s
'''))
