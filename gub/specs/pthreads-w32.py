from gub import misc
from gub import targetbuild

class Pthreads_w32 (targetbuild.MakeBuild):
    source = 'ftp://sourceware.org/pub/pthreads-win32/pthreads-w32-2-8-0-release.tar.gz'
    def makeflags (self):
        return 'GC CROSS=%(toolchain_prefix)s'
    def install_command (self):
        return misc.join_lines ('''
install -d %(install_prefix)s/bin
install -d %(install_prefix)s/include
install -d %(install_prefix)s/lib
&& install -m644 pthread.h sched.h %(install_prefix)s/include
&& install -m755 pthreadGC2.dll %(install_prefix)s/bin
&& install -m755 libpthreadGC2.a %(install_prefix)s/lib
&& install -m755 pthreadGC2.dll %(install_prefix)s/bin/pthread.dll
&& install -m755 libpthreadGC2.a %(install_prefix)s/lib/libpthread.a
''')
    def install (self):
        for file in ['pthread.h', 'sched.h']:
            self.file_sub ([('#undef PTW32_LEVEL\s', ''' 
#ifndef _POSIX_SOURCE
#define _POSIX_SOURCE
#undef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 199000
/*URG*/
#define pid_t int
#endif

#undef PTW32_LEVEL
''')],
                           '%(builddir)s/%(file)s', env=locals ())
        self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
''')
        self.install_license ()
        self.libtool_installed_la_fixups ()
