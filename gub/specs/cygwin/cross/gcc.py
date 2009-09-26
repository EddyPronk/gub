#
from gub.specs.cross import gcc as cross_gcc
from gub import cygwin
from gub import misc

# http://gcc.gnu.org/PR24196
class this_works_but_has_string_exception_across_dll_bug_Gcc__cygwin (cross_gcc.Gcc__mingw):
    dependencies = (cross_gcc.Gcc__mingw.dependencies
                    + ['cygwin', 'w32api-in-usr-lib'])
    configure_flags = (cross_gcc.Gcc__mingw.configure_flags
                       + misc.join_lines ('''
--with-newlib
--enable-threads
'''))
    make_flags = misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
gcc_tooldir="%(cross_prefix)s/%(target_architecture)s"
''')

class Gcc__cygwin (cross_gcc.Gcc):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-3.4.4/gcc-3.4.4.tar.bz2'
    patches = ['gcc-3.4.4-cygwin-3.patch']
    dependencies = (cross_gcc.Gcc.dependencies
                    + ['cygwin', 'w32api-in-usr-lib'])
    # We must use --with-newlib, otherwise configure fails:
    # No support for this host/target combination.
    # [configure-target-libstdc++-v3]
    configure_flags = (cross_gcc.Gcc.configure_flags
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
    def xuntar (self):
        ball = self.source._file_name ()
        cygwin.untar_cygwin_src_package_variant2 (self, ball.replace ('-core', '-g++'),
                                                  split=True)
        cygwin.untar_cygwin_src_package_variant2 (self, ball)
    make_flags = misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
gcc_tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
