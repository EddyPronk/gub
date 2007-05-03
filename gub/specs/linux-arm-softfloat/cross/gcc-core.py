from gub import mirrors
from gub import misc
gcc = misc.load_spec ('cross/gcc-core')

class Gcc_core (gcc.Gcc_core):
    def __init__ (self, settings):
        gcc.Gcc_core.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnu, version='3.4.6', format='bz2',
                           name='gcc')
    def patch (self):
        gcc.Gcc_core.patch (self)
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-3.4.0-arm-lib1asm.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-3.4.0-arm-nolibfloat.patch
''')
    def configure_command (self):
        return (gcc.Gcc_core.configure_command (self)
                + misc.join_lines ('''
--with-float=soft
#--with-fpu=vfp
'''))

