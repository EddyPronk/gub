from gub import mirrors
from gub.specs.cross import gcc
from gub import misc

class Gcc (gcc.Gcc):
    def __init__ (self, settings):
        gcc.Gcc.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnu, version='3.4.6', format='bz2')
    def patch (self):
        gcc.Gcc.patch (self)
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-3.4.0-arm-lib1asm.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-3.4.0-arm-nolibfloat.patch
''')
    def configure_command (self):
        return (gcc.Gcc.configure_command (self)
                + misc.join_lines ('''
--with-float=soft
#--with-fpu=vfp
'''))

