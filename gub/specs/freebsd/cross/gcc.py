from gub.specs.cross import gcc as cross_gcc
from gub import misc

class Gcc__freebsd (cross_gcc.Gcc):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-4.3.2/gcc-4.3.2.tar.bz2'
    dependencies = cross_gcc.Gcc.dependencies + ['tools::mpfr']
    def configure_command (self):
        return (cross_gcc.Gcc.configure_command (self)
                + misc.join_lines ('''
--program-prefix=%(toolchain_prefix)s
'''))
