from gub import gnome
from gub import misc
from gub import tools
from gub import target
from gub import w32

class Glib (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.26/2.26.3/sources/glib-2.20.4.tar.gz'
    dependencies = ['tools::glib', 'tools::libtool', 'gettext-devel']
    def config_cache_overrides (self, string):
        return string + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
    def install (self):
        target.AutoBuild.install (self)
        self.system ('rm -f %(install_prefix)s/lib/charset.alias')
        
class Glib__darwin (Glib):
    def configure (self):
        Glib.configure (self)
        self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
                       '%(builddir)s/libtool')

class Glib__darwin__x86 (Glib__darwin):
    def compile (self):
        self.file_sub ([('(SUBDIRS = .*) tests', r'\1'),
                        (r'GTESTER = \$.*', ''),
                        ('(am__EXEEXT(_[0-9])? = )gtester.*', r'\1'),
                        ('(am__append(_[0-9])? = )gtester', r'\1')],
                       '%(builddir)s/glib/Makefile', must_succeed=True)
        Glib__darwin.compile (self)
        
class Glib__mingw (Glib):
    dependencies = Glib.dependencies + ['libiconv-devel']
    def update_libtool (self): # linux-x86, linux-ppc, freebsd-x86
        target.AutoBuild.update_libtool (self)
        self.map_locate (w32.libtool_disable_relink, '%(builddir)s', 'libtool')

class Glib__freebsd (Glib):
    dependencies = Glib.dependencies + ['libiconv-devel']
    configure_variables = Glib.configure_variables + ' CFLAGS=-pthread'

class Glib__freebsd__x86 (Glib__freebsd):
    # Must include -pthread in lib flags, because our most beloved
    # libtool (2.2.6a) thinks it knows best and blondly strips -pthread
    # if it thinks it's a compile flag.
    # FIXME: should add fixup to update_libtool ()
    make_flags = ' G_THREAD_LIBS=-pthread G_THREAD_LIBS_FOR_GTHREAD=-pthread '

class Glib__tools (tools.AutoBuild, Glib):
    dependencies = [
            'gettext',
            'libtool',
            ]            
    def install (self):
        tools.AutoBuild.install (self)
        self.system ('rm -f %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/lib/charset.alias')
