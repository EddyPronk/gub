from gub import cross
from gub import misc
from gub import mirrors
from gub import context
from gub import loggedos

#FIXME: merge fully with specs/gcc
class Gcc (cross.CrossToolsBuild):
    source = mirrors.with_tarball (mirror=mirrors.gcc, version='4.1.1', format='bz2', name='gcc')

    def get_build_dependencies (self):
        return ['cross/binutils']

    @context.subst_method
    def NM_FOR_TARGET(self):
         return '%(toolchain_prefix)snm'

    def get_subpackage_names (self):
        # FIXME: why no -devel package?
        return ['doc', 'runtime', '']

    def languages (self):
        return ['c', 'c++']
        
    def configure_command (self):
        cmd = cross.CrossToolsBuild.configure_command (self)
        # FIXME: using --prefix=%(tooldir)s makes this
        # uninstallable as a normal system package in
        # /usr/i686-mingw/
        # Probably --prefix=/usr is fine too

        language_opt = (' --enable-languages=%s '
                        % ','.join (self.languages ()))
        cxx_opt = '--enable-libstdcxx-debug '

        cmd += '''
--with-as=%(cross_prefix)s/bin/%(target_architecture)s-as
--with-ld=%(cross_prefix)s/bin/%(target_architecture)s-ld
--enable-static
--enable-shared '''

        cmd += language_opt
        if 'c++' in self.languages ():
            cmd +=  ' ' + cxx_opt

        return misc.join_lines (cmd)

    def move_target_libs (self, libdir):
        self.system ('mkdir -p %(install_prefix)s/lib || true')

        ## .so* because version numbers trail .so extension.
        for suf in ['.la', '.so*', '.dylib']:
            # todo: maplocate
            self.system("""
find %(libdir)s -name 'lib*%(suf)s' -exec mv '{}' %(install_prefix)s/lib ';'
""", locals())

    def install (self):
        cross.CrossToolsBuild.install (self)
        old_libs = self.expand ('%(install_prefix)s/cross/%(target_architecture)s')

        self.move_target_libs (old_libs)
        self.move_target_libs (self.expand ('%(install_prefix)s/cross/lib'))

class Gcc__from__source (Gcc):
    def get_build_dependencies (self):
        return (Gcc.get_build_dependencies (self)
                + ['cross/gcc-core', 'glibc-core'])
    def get_conflict_dict (self):
        return {'': ['cross/gcc-core'], 'doc': ['cross/gcc-core'], 'runtime': ['cross/gcc-core']}
    #FIXME: merge all configure_command settings with Gcc
    def configure_command (self):
        return (Gcc.configure_command (self)
                + misc.join_lines ('''
--with-local-prefix=%(system_prefix)s
--disable-multilib
--disable-nls
--enable-threads=posix
--enable-__cxa_atexit
--enable-symvers=gnu
--enable-c99 
--enable-clocale=gnu 
--enable-long-long
'''))
    def install (self):
        Gcc.install (self)
        self.system ('''
mv %(install_prefix)s/cross/lib/gcc/%(target_architecture)s/%(version)s/libgcc_eh.a %(install_prefix)s/lib
''')

Gcc__linux = Gcc__from__source

class Gcc__mingw (Gcc):
    #REMOVEME
    def __init__ (self, settings, source):
        Gcc.__init__ (self, settings, source)
    source = mirrors.with_tarball (name='gcc', mirror=mirrors.gnu, version='4.1.1', format='bz2')
    def get_build_dependencies (self):
        return (Gcc.get_build_dependencies (self)
                + ['mingw-runtime', 'w32api'])
    def patch (self):
        for f in ['%(srcdir)s/gcc/config/i386/mingw32.h',
                  '%(srcdir)s/gcc/config/i386/t-mingw32']:
            self.file_sub ([('/mingw/include','%(prefix_dir)s/include'),
                            ('/mingw/lib','%(prefix_dir)s/lib'),
                            ], f)

class Gcc__cygwin (Gcc__mingw):
    def get_build_dependencies (self):
        return (Gcc__mingw.get_build_dependencies (self)
                + ['cygwin', 'w32api-in-usr-lib'])
    def makeflags (self):
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
gcc_tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def compile_command (self):
        return (Gcc__mingw.compile_command (self)
                + self.makeflags ())
    def configure_command (self):
        # We must use --with-newlib, otherwise configure fails:
        # No support for this host/target combination.
        # [configure-target-libstdc++-v3]
        return (Gcc__mingw.configure_command (self)
                + misc.join_lines ('''
--with-newlib
--enable-threads
'''))

from gub import cygwin

class use_cygwin_sources_Gcc__cygwin (Gcc):
    def __init__ (self, settings, source):
        Gcc.__init__ (self, settings, source)
    source = mirrors.with_tarball (mirror=mirrors.cygwin, version='3.4.4-3', format='bz2', name='gcc')
    def name (self):
        return 'cross/gcc-core'
    def untar (self):
        #gxx_file_name = re.sub ('-core', '-g++',
        #                        self.expand (self.file_name ()))
#        ball = 'cross/' + self.source._file_name ().replace ('gcc', 'gcc-core')
        ball = self.source._file_name ()
        cygwin.untar_cygwin_src_package_variant2 (self, ball.replace ('-core', '-g++'),
                                                  split=True)
        cygwin.untar_cygwin_src_package_variant2 (self, ball)
    def get_build_dependencies (self):
        return (Gcc.get_build_dependencies (self)
                + ['cygwin', 'w32api-in-usr-lib', 'cross/gcc-g++'])
    def makeflags (self):
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
gcc_tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def configure_command (self):
        # We must use --with-newlib, otherwise configure fails:
        # No support for this host/target combination.
        # [configure-target-libstdc++-v3]
        return (Gcc.configure_command (self)
                + misc.join_lines ('''
--with-newlib
--verbose
--enable-nls
--without-included-gettext
--enable-version-specific-runtime-libs
--without-x
--enable-libgcj
--with-system-zlib
--enable-interpreter
--disable-libgcj-debug
--enable-threads=posix
--disable-win32-registry
--enable-sjlj-exceptions
--enable-hash-synchronization
--enable-libstdcxx-debug
'''))

class Gcc__darwin (Gcc):
    #FIXME: what about apply_all (%(patchdir)s/%(version)s)?
    def patch (self):
        if self.source._version == '4.1.1':
            self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-4.1.1-ppc-unwind.patch
''')

class Gcc__freebsd (Gcc):
    #REMOVEME
    def __init__ (self, settings, source):
        Gcc.__init__ (self, settings, source)
    source = mirrors.with_tarball (name='gcc', mirror=mirrors.gnu, version='4.1.1', format='bz2')
    def get_build_dependencies (self):
        return (Gcc.get_build_dependencies (self)
                + ['freebsd-runtime'])
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        return (Gcc.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(toolchain_prefix)s
'''))
