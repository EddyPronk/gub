from gub import gnome
from gub import target

class Atk (target.AutoBuild):
    source = gnome.platform_url ('atk')
    dependencies = ['tools::libtool', 'glib-devel']

class Atk__mingw (Atk):
    def patch (self):
        self.file_sub ([('\$\(srcdir\)/atk.def', 'atk.def')], '%(srcdir)s/atk/Makefile.in', must_succeed=True)
