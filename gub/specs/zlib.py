import re
#
from gub import build
from gub import target
from gub import tools

class Zlib (target.AutoBuild):
    source = 'http://heanet.dl.sourceforge.net/sourceforge/libpng/zlib-1.2.3.tar.gz'
    patches = ['zlib-1.2.3.patch']
    def get_build_dependencies (self):
        return ['tools::autoconf']
    def configure (self):
        self.shadow ()
        target.AutoBuild.configure (self)
    def compile_command (self):
        return target.AutoBuild.compile_command (self) + ' ARFLAGS=r '
    def configure_command (self):
        stripped_platform = self.settings.expand ('%(platform)s')
        stripped_platform = re.sub ('-.*', '', stripped_platform)
        stripped_platform = stripped_platform.replace ('darwin', 'Darwin')
        
        zlib_is_broken = 'SHAREDTARGET=libz.so.1.2.3 target=' + stripped_platform
        ## doesn't use autoconf configure.
        return zlib_is_broken + ' %(srcdir)s/configure --shared '
    def install_command (self):
        return target.AutoBuild.broken_install_command (self)
    def license_files (self):
        return ['%(sourcefiledir)s/zlib.license']

class Zlib_plain__mingw (Zlib):
    patches = Zlib.patches
    def patch (self):
        Zlib.patch (self)
        self.file_sub ([("='/bin/true'", "='true'"),
                        ('mgwz','libz'),
                        ],
                       '%(srcdir)s/configure')
    def configure_command (self):
        zlib_is_broken = 'target=mingw'
        return zlib_is_broken + ' %(srcdir)s/configure --shared '

class Zlib_minizip__mingw (Zlib_plain__mingw):
    patches = Zlib_plain__mingw.patches
    def patch_include_minizip (self):
        self.file_sub ([('(inffast.o)$', r'\1 ioapi.o iowin32.o mztools.o unzip.o zip.o\nVPATH= contrib/minizip\n')],
                   '%(srcdir)s/Makefile.in')
    def install_include_minizip (self):
        self.system ('cd %(srcdir)s/contrib/minizip && cp ioapi.h iowin32.h mztools.h unzip.h zip.h %(install_prefix)s/include')
    def patch (self):
        Zlib_plain__mingw.patch (self)
        self.patch_include_minizip ()
    def configure_command (self):
        return ''' CFLAGS='-I. -O3' ''' + Zlib_plain__mingw.configure_command (self)
    def install (self):
        Zlib_plain__mingw.install (self)
        self.install_include_minizip ()

Zlib__mingw = Zlib_minizip__mingw

class Zlib__freebsd__64 (Zlib):
    pass
'''
no shared lib: gcc-4.2.1 says
./home/janneke/tmp/python-mingw/target/freebsd-64/root/usr/cross/bin/x86_64-freebsd6-ld: error in /home/janneke/tmp/python-mingw/target/freebsd-64/root/usr/cross/lib/gcc/x86_64-freebsd6/4.1.2/crtendS.o(.eh_frame); no .eh_frame_hdr table will be created..
'''

class Zlib__tools (tools.AutoBuild, Zlib):
    source = Zlib.source
# FIXME: tools not the same as target: asking for trouble
#    source = 'http://heanet.dl.sourceforge.net/sourceforge/libpng/zlib-1.2.3.3.tar.gz'
# FIXME: where lives 1.2.3.3 with gzopen64?
    patches = Zlib.patches
    def get_build_dependencies (self):
        return ['autoconf']
    def configure (self):
        self.shadow ()
        tools.AutoBuild.configure (self)
    def install_command (self):
        return tools.AutoBuild.broken_install_command (self)
    def configure_command (self):
        return Zlib.configure_command (self)
    def license_files (self):
        return ['%(sourcefiledir)s/zlib.license']
