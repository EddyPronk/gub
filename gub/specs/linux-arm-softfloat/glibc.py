from gub import misc
from gub.specs import glibc

class Glibc (glibc.Glibc):
    def patch (self):
        glibc.Glibc.patch (self)
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3-wordexp-inline.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3-linux-2.4.23-arm-bus-isa.patch
''')
    def enable_add_ons (self):
        return (glibc.Glibc.enable_add_ons (self)
                .replace ('--enable-add-ons=nptl', ''))
    configure_variables = (glibc.Glibc.configure_variables
                           + ' --without-fp')
