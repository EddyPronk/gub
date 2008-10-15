from gub.specs.cross import binutils

class Binutils__freebsd (binutils.Binutils):
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        from gub import misc
        return (binutils.Binutils.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(toolchain_prefix)s
'''))
