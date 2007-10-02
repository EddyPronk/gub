import re
import os

from gub import mirrors
from gub import misc
from gub import targetbuild

class Libjpeg (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
    source = mirrors.with_template (name='libjpeg', version='v6b', mirror=mirrors.jpeg)

    def name (self):
        return 'libjpeg'

    def get_build_dependencies (self):
        return ['libtool']

    def get_subpackage_names (self):
        return ['devel', '']
    
    def srcdir (self):
        return re.sub (r'src\.v', '-', targetbuild.TargetBuild.srcdir(self))

    def configure_command (self):
        return (targetbuild.TargetBuild.configure_command (self)
                .replace ('--config-cache', '--cache-file=config.cache'))
    
    def update_libtool (self):
        self.system ('''
cd %(builddir)s && %(srcdir)s/ltconfig --srcdir %(srcdir)s %(srcdir)s/ltmain.sh %(target_architecture)s'''
              , locals ())
        
        targetbuild.TargetBuild.update_libtool (self)

    def license_file (self):
        return '%(sourcefiledir)s/jpeg.license'

    def configure (self):
        guess = self.expand ('%(system_prefix)s/share/libtool/config.guess')
        sub = self.expand ('%(system_prefix)s/share/libtool/config.sub')
        for file in sub, guess:
            if os.path.exists (file):
                self.system ('cp -pv %(file)s %(srcdir)s',  locals ())

        targetbuild.TargetBuild.configure (self)
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
        targetbuild.TargetBuild.update_libtool (self)

class Libjpeg__mingw (Libjpeg):
    def configure (self):
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
