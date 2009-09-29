from gub import gnome
from gub import target

class Atk (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.26/2.26.3/sources/atk-1.26.0.tar.gz'
    dependencies = ['tools::libtool', 'glib-devel']

class Atk__mingw (Atk):
    def patch (self):
        self.file_sub ([('\$\(srcdir\)/atk.def', 'atk.def')], '%(srcdir)s/atk/Makefile.in', must_succeed=True)
