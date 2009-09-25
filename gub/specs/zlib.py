import re
#
from gub import context
from gub import target
from gub import tools

class Zlib (target.AutoBuild):
    source = 'http://heanet.dl.sourceforge.net/sourceforge/libpng/zlib-1.2.3.tar.gz'
    patches = ['zlib-1.2.3.patch']
    srcdir_build_broken = True
    dependencies = ['tools::autoconf']
    make_flags = ' ARFLAGS=r'
    destdir_install_broken = True
    install_flags = ' install'
    @context.subst_method
    def zlib_target (self):
        stripped_platform = self.settings.expand ('%(platform)s')
        stripped_platform = re.sub ('-.*', '', stripped_platform)
        stripped_platform = stripped_platform.replace ('darwin', 'Darwin')
        return 'SHAREDTARGET=libz.so.1.2.3 target=' + stripped_platform
    def configure_command (self):
        return '%(zlib_target)s %(srcdir)s/configure --shared '
    def license_files (self):
        return ['%(sourcefiledir)s/zlib.license']

class Zlib_plain__mingw (Zlib):
    def patch (self):
        Zlib.patch (self)
        self.file_sub ([("='/bin/true'", "='true'"),
                        ('mgwz','libz'),
                        ],
                       '%(srcdir)s/configure')
    def configure_command (self):
        return '%(zlib_target)s %(srcdir)s/configure --shared '
    def zlib_target (self):
        return 'target=mingw'

class Zlib_minizip__mingw (Zlib_plain__mingw):
    def configure_command (self):
        return (''' CFLAGS='-I. -O3' '''
                + Zlib_plain__mingw.configure_command (self))
    def patch_include_minizip (self):
        self.file_sub ([('(inffast.o)$', r'\1 ioapi.o iowin32.o mztools.o unzip.o zip.o\nVPATH= contrib/minizip\n')],
                   '%(srcdir)s/Makefile.in')
    def install_include_minizip (self):
        self.system ('cd %(srcdir)s/contrib/minizip && cp ioapi.h iowin32.h mztools.h unzip.h zip.h %(install_prefix)s/include')
    def patch (self):
        Zlib_plain__mingw.patch (self)
        self.patch_include_minizip ()
    def install (self):
        Zlib_plain__mingw.install (self)
        self.install_include_minizip ()

Zlib__mingw = Zlib_minizip__mingw

class Zlib__freebsd__64 (Zlib):
    patches = []
'''
no shared lib: gcc-4.2.1 says
./home/janneke/tmp/python-mingw/target/freebsd-64/root/usr/cross/bin/x86_64-freebsd6-ld: error in /home/janneke/tmp/python-mingw/target/freebsd-64/root/usr/cross/lib/gcc/x86_64-freebsd6/4.1.2/crtendS.o(.eh_frame); no .eh_frame_hdr table will be created..
'''

class Zlib__tools (tools.AutoBuild, Zlib):
    srcdir_build_broken = True
    dependencies = ['autoconf']
    configure_command = Zlib.configure_command
    destdir_install_broken = True
    install_flags = ' install'
    license_files = Zlib.license_files
