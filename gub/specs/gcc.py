from gub import loggedos
from gub import system
from gub import tools

class Gcc__system (system.Configure):
    def description (self):
        return 'GNU C compiler; 4.x is strongly recommended'

class Gcc__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.2/gcc-4.1.2.tar.bz2'
    def _get_build_dependencies (self):
        return [
            'binutils',
            ]
    def patch (self):
        tools.AutoBuild.patch (self)
        do_not_look_in_slash_usr (self)
    def languages (self):
        return ['c', 'c++']
    def configure_variables (self):
        return ''
    def configure_command (self):
        # FIXME: using --prefix=%(tooldir)s makes this
        # uninstallable as a normal system package in
        # /usr/i686-mingw/
        # Probably --prefix=/usr is fine too
        enable_libstdcxx_debug = ''
        if 'c++' in self.languages ():
            enable_libstdcxx_debug = ' --enable-libstdcxx-debug'
        return (tools.AutoBuild.configure_command (self)
                + ' --enable-languages=' + ','.join (self.languages ())
# python2.5-ism
#                + ' --enable-libstdcxx-debug' if 'c++' in self.languages () else ''
                + enable_libstdcxx_debug
                + ' --disable-multilib'
                + ' --enable-static'
                + ' --enable-shared'
                + ' --with-as=%(tools_prefix)s/bin/as'
                + ' --with-ld=%(tools_prefix)s/bin/ld'
                + ' --with-nm=%(tools_prefix)s/bin/nm'
                )
    def makeflags (self):
        return (
            ' tooldir="%(cross_prefix)s/%(target_architecture)s"'
            + ' gcc_tooldir="%(prefix_dir)s/%(target_architecture)s"'
            )
    def install (self):
        tools.AutoBuild.install (self)
        move_target_libs (self, '%(install_prefix)s/%(target_architecture)s')
#        move_target_libs ('%(install_prefix)s%/lib')
        self.disable_libtool_la_files ('libstdc[+][+]')

def do_not_look_in_slash_usr (self):
    # GUB [cross] compilers must NOT look in /usr.
    # Fixes LIBRESTRICT=stat:open and resulting ugliness.
    for i in ['%(srcdir)s/configure', '%(srcdir)s/gcc/configure']:
        self.file_sub ([
                # gcc-4.1.1 gcc/configure
                ('( *gcc_cv_tool_dirs=.*PATH_SEPARATOR/usr)', r'#\1'), 
                # gcc-4.3.2 ./configure
                ('( *gcc_cv_tool_dirs=.*gcc_cv_tool_dirs/usr)', r'#\1')],
                       i)
        # This seems to have been fixed in gcc-4.3.2, but only if
        # *not* cross-compiling---a hardcoded lookup in /usr, without
        # asking configure, still makes no sense to me.  Redirecting
        # lookups survives gcc-4.1.1--4.3.2, which is more robust than
        # patching them out.
        self.file_sub ([
                ('( standard_exec_prefix_.*= ")/usr', r'\1%(system_prefix)s')],
                       '%(srcdir)s/gcc/gcc.c')

def move_target_libs (self, libdir):
    self.system ('mkdir -p %(install_prefix)s/lib || true')
    def move_target_lib (logger, file_name):
        base = os.path.split (self.expand (file_name))[1]
        loggedos.rename (logger, file_name, os.path.join (self.expand ('%(install_prefix)s/lib'), base))
#        for suf in ['.la', '.so*', '.dylib']:
        # .so* because version numbers trail .so extension.
    for suf in ['.a', '.la', '.so*', '.dylib']:
        self.map_find_files (move_target_lib, libdir, 'lib.*%(suf)s' % locals ())
