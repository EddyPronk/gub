from gub.specs.cross import binutils
from gub import misc

class Binutils__freebsd (binutils.Binutils):
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        return (binutils.Binutils.configure_command (self)
                # PROMOTEME: if this work, try removing from cross.py
                .replace ('LDFLAGS=-L%(system_prefix)s/lib', '')
                + misc.join_lines ('''
--program-prefix=%(toolchain_prefix)s
'''))
