import os
import re
#
from gub import commands
from gub import misc
from gub import targetbuild
from gub import toolsbuild

class Libjpeg (targetbuild.AutoBuild):
    source = 'ftp://ftp.uu.net/graphics/jpeg/jpegsrc.v6b.tar.gz'
    def __init__ (self, settings, source):
        targetbuild.AutoBuild.__init__ (self, settings, source)
        source._version = 'v6b'

    def name (self):
        return 'libjpeg'

    def get_build_dependencies (self):
        return ['libtool']

    def get_subpackage_names (self):
        return ['devel', '']
    
    def srcdir (self):
        return re.sub (r'src\.v', '-', targetbuild.AutoBuild.srcdir (self))

    def configure_command (self):
        return (targetbuild.AutoBuild.configure_command (self)
                .replace ('--config-cache', '--cache-file=config.cache'))
    
    def update_libtool (self):
        self.system ('''
cd %(builddir)s && %(srcdir)s/ltconfig --srcdir %(srcdir)s %(srcdir)s/ltmain.sh %(target_architecture)s'''
              , locals ())
        targetbuild.AutoBuild.update_libtool (self)

    def license_files (self):
        return ['%(sourcefiledir)s/jpeg.license']

    def configure (self):
        guess = self.expand ('%(system_prefix)s/share/libtool/config.guess')
        sub = self.expand ('%(system_prefix)s/share/libtool/config.sub')
        for file in sub, guess:
            self.system ('cp -pv %(file)s %(srcdir)s',  locals ())

        targetbuild.AutoBuild.configure (self)
        self.update_libtool ()
        self.file_sub (
            [
            (r'(\(INSTALL_[A-Z]+\).*) (\$[^ ]+)$',
            r'\1 $(DESTDIR)\2'),
            ],
            '%(builddir)s/Makefile')

    def install_command (self):
        return misc.join_lines ('''
mkdir -p %(install_prefix)s/include %(install_prefix)s/lib
&& make DESTDIR=%(install_root)s install-headers install-lib
''')

class Libjpeg__darwin (Libjpeg):
    def update_libtool (self):
        arch = 'powerpc-apple'
        self.system ('''
cd %(builddir)s && %(srcdir)s/ltconfig --srcdir %(srcdir)s %(srcdir)s/ltmain.sh %(arch)s
''', locals ())
        targetbuild.AutoBuild.update_libtool (self)

class Libjpeg__mingw (Libjpeg):
    def xxconfigure (self):
        Libjpeg.configure (self)
        # libtool will not build dll if -no-undefined flag is
        # not present
        self.file_sub ([('-version-info',
                '-no-undefined -version-info')],
             '%(builddir)s/Makefile')

class Libjpeg__linux (Libjpeg):
    def compile (self):
        Libjpeg.compile (self)
        self.file_sub ([('^#define (HAVE_STDLIB_H) *', '''#ifdef \\1
#define \\1
#endif''')],
               '%(builddir)s/jconfig.h')

class Libjpeg__tools (toolsbuild.AutoBuild):
    source = Libjpeg.source
    def __init__ (self, settings, source):
        toolsbuild.AutoBuild.__init__ (self, settings, source)
        source._version = 'v6b'
    def get_build_dependencies (self):
        return ['libtool']
    def srcdir (self):
        return re.sub (r'src\.v', '-', toolsbuild.AutoBuild.srcdir (self))
    def force_autoupdate (self):
        return True
    def configure (self):
        toolsbuild.AutoBuild.configure (self)
        self.update_libtool ()
        self.file_sub (
            [
                (r'(\(INSTALL_[A-Z]+\).*) (\$[^ ]+)$',
                 r'\1 $(DESTDIR)\2'),
                ],
            '%(builddir)s/Makefile')
    def install_command (self):
        return misc.join_lines ('''
mkdir -p %(install_root)s/%(system_prefix)s/bin %(install_root)s/%(system_prefix)s/include %(install_root)s/%(system_prefix)s/lib 
&& make DESTDIR=%(install_root)s install-headers install-lib
''')
