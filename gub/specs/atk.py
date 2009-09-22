from gub import gnome
from gub import target

class Atk (target.AutoBuild):
    #source = 'ftp://ftp.gnome.org/pub/GNOME/sources/atk/1.25/atk-1.25.2.tar.gz'
    #source = 'ftp://ftp.gnome.org/pub/GNOME/sources/atk/1.25/atk-1.25.2.tar.gz&dependency=tools::libtool&dependency=glib-devel'
    source = gnome.platform_url ('atk')
    build_dependencies = ['tools::libtool', 'glib-devel']
    def XX_get_build_dependencies (self):
        return ['tools::libtool', 'glib-devel']

class Atk__mingw (Atk):
    def patch (self):
        self.file_sub ([('\$\(srcdir\)/atk.def', 'atk.def')], '%(srcdir)s/atk/Makefile.in', must_succeed=True)
