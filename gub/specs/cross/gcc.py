import os
#
from gub import cross
from gub import cygwin
from gub import misc
from gub import context
from gub import loggedos

#FIXME: merge fully with specs/gcc
class Gcc (cross.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.2/gcc-4.1.2.tar.bz2'
    def get_build_dependencies (self):
        return ['cross/binutils']
    def patch (self):
        cross.AutoBuild.patch (self)
        if False and self.settings.build_architecture == self.settings.target_architecture:
            # This makes the target build *not* use /lib* at all, but
            # it produces executables that will only run within the
            # build system, using something like
            #
            #    x86_64-linux-gcc -Wl,-rpath -Wl,\$ORIGIN/../lib -Wl,-rpath -Wl,/home/janneke/vc/gub/target/linux-64/root/usr/lib foo.c
            #
            # which means that we *must* distribute libc, which we
            # probably don't want to do.
            self.file_sub ([('DYNAMIC_LINKER "/lib', 'DYNAMIC_LINKER "%(system_prefix)s/lib')],
                           '%(srcdir)s/gcc/config/i386/linux.h')
            self.file_sub ([('-dynamic-linker /lib64', '-dynamic-linker %(system_prefix)s/lib')],
                           '%(srcdir)s/gcc/config/i386/linux64.h')
    @context.subst_method
    def NM_FOR_TARGET (self):
         return '%(toolchain_prefix)snm'
    def get_subpackage_names (self):
        # FIXME: why no -devel package?
        return ['doc', 'runtime', '']
    def languages (self):
        return ['c', 'c++']
    def configure_command (self):
        cmd = cross.AutoBuild.configure_command (self)
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
--with-nm=%(cross_prefix)s/bin/%(target_architecture)s-nm
--enable-static
--enable-shared '''
        cmd += language_opt
        if 'c++' in self.languages ():
            cmd +=  ' ' + cxx_opt
        return misc.join_lines (cmd)
    def makeflags (self):
        return misc.join_lines ('''
toolexeclibdir=%(system_prefix)s
GUB_FLAGS_TO_PASS='toolexeclibdir=$(toolexeclibdir)'
RECURSE_FLAGS_TO_PASS='$(BASE_FLAGS_TO_PASS) $(GUB_FLAGS_TO_PASS)'
FLAGS_TO_PASS='$(BASE_FLAGS_TO_PASS) $(EXTRA_HOST_FLAGS) $(GUB_FLAGS_TO_PASS)'
TARGET_FLAGS_TO_PASS='$(BASE_FLAGS_TO_PASS) $(EXTRA_TARGET_FLAGS) $(GUB_FLAGS_TO_PASS)'
''')
    def UGH_TRY_SETTING_toolexeclibdir_in_MAKEFLAGS_move_target_libs (self, libdir):
        self.system ('mkdir -p %(install_prefix)s/lib || true')
        def move_target_lib (logger, file_name):
            base = os.path.split (file_name)[1]
            loggedos.rename (logger, file_name, os.path.join (self.expand ('%(install_prefix)s/lib'), base))
            #loggedos.system (logger, 'echo NOT mv %(file_name)s '% locals () + os.path.join (self.expand ('%(install_prefix)s/lib'), base))
#        for suf in ['.la', '.so*', '.dylib']:
        # .so* because version numbers trail .so extension.
        for suf in ['.a', '.la', '.so*', '.dylib']:
            self.map_locate (move_target_lib, libdir, 'lib*%(suf)s' % locals ())
    # URGME: what about toolexeclibdir?
    def UGH_TRY_SETTING_toolexeclibdir_in_MAKEFLAGS_install (self):
        cross.AutoBuild.install (self)
        self.move_target_libs (self.expand ('%(install_root)s/%(cross_prefix)s/%(target_architecture)s'))
        self.move_target_libs (self.expand ('%(install_root)s/%(cross_prefix)s/lib'))

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

class Gcc__linux__64 (Gcc__linux):
    def install (self):
        Gcc__linux.install (self)
        self.system ('false')

class Gcc__mingw (Gcc):
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.1/gcc-4.1.1.tar.bz2'

    def get_build_dependencies (self):
        return (Gcc.get_build_dependencies (self)
                + ['mingw-runtime', 'w32api'])
    def patch (self):
        for f in ['%(srcdir)s/gcc/config/i386/mingw32.h',
                  '%(srcdir)s/gcc/config/i386/t-mingw32']:
            self.file_sub ([('/mingw/include','%(prefix_dir)s/include'),
                            ('/mingw/lib','%(prefix_dir)s/lib'),
                            ], f)
    # Possibly update libtool for mingw at least?  Try setting toolexeclibdir first...
    def XXXinstall (self):
        Gcc.install (self)
        # libtool barfs: no libstdc++.dll.a file
        self.system ('''
mv %(install_prefix)s/lib/libstdc++.la %(install_prefix)s/lib/libstdc++.la-
''')

# http://gcc.gnu.org/PR24196            
class this_works_but_has_string_exception_across_dll_bug_Gcc__cygwin (Gcc__mingw):
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

# Cygwin sources Gcc
# Hmm, download is broken.  How is download of gcc-g++ supposed to work anyway?
# wget http://mirrors.kernel.org/sourceware/cygwin/release/gcc/gcc-core/gcc-core-3.4.4-3-src.tar.bz2 
# wget http://mirrors.kernel.org/sourceware/cygwin/release/gcc/gcc-g++/gcc-g++-3.4.4-3-src.tar.bz2

# Untar stage is gone, use plain gcc + cygwin patch
#class Gcc__cygwin (Gcc):
class Gcc__cygwin (Gcc):
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-3.4.4/gcc-3.4.4.tar.bz2'
    patches = ['gcc-3.4.4-cygwin-3.patch']
    def xuntar (self):
        ball = self.source._file_name ()
        cygwin.untar_cygwin_src_package_variant2 (self, ball.replace ('-core', '-g++'),
                                                  split=True)
        cygwin.untar_cygwin_src_package_variant2 (self, ball)
    def get_build_dependencies (self):
        return (Gcc.get_build_dependencies (self)
#                + ['cygwin', 'w32api-in-usr-lib', 'cross/gcc-g++'])
                + ['cygwin', 'w32api-in-usr-lib'])
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
