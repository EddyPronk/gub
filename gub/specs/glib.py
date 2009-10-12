from gub import gnome
from gub import misc
from gub import tools
from gub import target
from gub import w32

class Glib (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.26/2.26.3/sources/glib-2.20.4.tar.gz'
    ##source = 'http://ftp.gnome.org/pub/GNOME/platform/2.25/2.25.5/sources/glib-2.19.5.tar.gz'
    dependencies = ['tools::glib', 'tools::libtool', 'gettext-devel']
    config_cache_overrides = target.AutoBuild.config_cache_overrides + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
    if 'stat' in misc.librestrict (): # stats for /USR/include/glib/...
        install_flags = (target.AutoBuild.install_flags
                         + ' LD_PRELOAD=%(tools_prefix)s/lib/librestrict-open.so')
    def update_libtool (self): # linux-x86, linux-ppc, freebsd-x86
        target.AutoBuild.update_libtool (self)
        self.map_locate (w32.libtool_disable_relink, '%(builddir)s', 'libtool')
        #URGME, 2.19.5: relinking libgio is broken, /usr/lib is inserted
        '''root/usr/lib/usr/lib -L/usr/lib -lgobject-2.0 -L/home/janneke/vc/gub/target/linux-ppc/install/glib-2.19.5-root/usr/lib/home/janneke/vc/gub/target/linux-ppc/build/glib-2.19.5/gmodule/.libs -lgmodule-2.0 -ldl -lglib-2.0    -Wl,-soname -Wl,libgio-2.0.so.0 -Wl,-version-script -Wl,.libs/libgio-2.0.ver -o .libs/libgio-2.0.so.0.1905.0
/home/janneke/vc/gub/target/linux-ppc/root/usr/cross/bin/powerpc-linux-ld: skipping incompatible /usr/lib/libgobject-2.0.so when searching for -lgobject-2.0
/home/janneke/vc/gub/target/linux-ppc/root/usr/cross/bin/powerpc-linux-ld: skipping incompatible /usr/lib/libgobject-2.0.a when searching for -lgobject-2.0
/home/janneke/vc/gub/target/linux-ppc/root/usr/cross/bin/powerpc-linux-ld: cannot find -lgobject-2.0
collect2: ld returned 1 exit status
libtool: install: error: relink `libgio-2.0.la' with the above command before installing it
make[5]: *** [install-libLTLIBRARIES] Error 1
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
            'pkg-config',
            ]            
    configure_flags = (tools.AutoBuild.configure_flags
                       + ' --build=%(build_architecture)s'
                       + ' --host=%(build_architecture)s'
                       + ' --target=%(build_architecture)s'
                       )
    def install (self):
        tools.AutoBuild.install (self)
        self.system ('rm -f %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/lib/charset.alias')
