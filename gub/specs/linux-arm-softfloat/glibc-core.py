#from gub.specs import glibc-core
from gub import misc
glibc = misc.load_spec ('glibc-core')

class Glibc_core (glibc.Glibc_core):
    def patch (self):
        glibc.Glibc_core.patch (self)
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3-wordexp-inline.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3-linux-2.4.23-arm-bus-isa.patch
''')
    def configure_command (self):
        return (glibc.Glibc_core.configure_command (self)
                + misc.join_lines ('''
--without-fp
'''))
