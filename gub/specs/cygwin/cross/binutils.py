from gub.specs.cross import binutils

# FIXME: setting binutil's tooldir and/or gcc's gcc_tooldir may fix
# -luser32 (ie -L .../w32api/) problem without having to set LDFLAGS.
class Binutils (binutils.Binutils):
    def __init__ (self, settings):
        binutils.Binutils.__init__ (self, settings)
        from gub import mirrors
        self.with (version='2.17', format='bz2', mirror=mirrors.gnu)
    def makeflags (self):
        from gub import misc
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def compile_command (self):
        return (binutils.Binutils.compile_command (self)
                + self.makeflags ())
    def configure_command (self):
        return (binutils.Binutils.configure_command (self)
                 + ' --disable-werror ')
