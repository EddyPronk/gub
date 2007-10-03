from gub.specs.cross import binutils
from gub import cygwin
from gub import mirrors

# FIXME: setting binutil's tooldir and/or gcc's gcc_tooldir may fix
# -luser32 (ie -L .../w32api/) problem without having to set LDFLAGS.
class Binutils (binutils.Binutils):
    source = mirrors.with_template (name='binutils', version='2.17', format='bz2', mirror=mirrors.gnu)
    def makeflags (self):
        from gub import misc
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def configure_command (self):
        return (binutils.Binutils.configure_command (self)
                 + ' --disable-werror ')

class use_cygwin_sources_Binutils (binutils.Binutils):
    def __init__ (self, settings, source):
        binutils.Binutils.__init__ (self, settings, source)
        from gub import mirrors
    source = mirrors.with_template (name='binutils', version='20060817-1', format='bz2', mirror=mirrors.cygwin)
