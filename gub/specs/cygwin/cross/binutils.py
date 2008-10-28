from gub.specs.cross import binutils
from gub import cygwin

# FIXME: setting binutil's tooldir and/or gcc's gcc_tooldir may fix
# -luser32 (ie -L .../w32api/) problem without having to set LDFLAGS.
class Binutils (binutils.Binutils):
    source = 'ftp://ftp.gnu.org/pub/gnu/binutils/binutils-2.17.tar.bz2'
    def makeflags (self):
        from gub import misc
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def configure_command (self):
        return (binutils.Binutils.configure_command (self)
                 + ' --disable-werror ')

class use_cygwin_sources_Binutils (binutils.Binutils):
    source = 'http://mirrors.kernel.org/sourceware/cygwin/release/binutils/binutils-20060817-1-src.tar.bz2'
