import os
import re
#
from gub import commands
from gub import misc
from gub import target
from gub import tools

class Libjpeg (target.AutoBuild):
    source = 'ftp://ftp.uu.net/graphics/jpeg/jpegsrc.v6b.tar.gz'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        source._version = 'v6b'
    def name (self):
        return 'libjpeg'
    def _get_build_dependencies (self):
        return ['libtool']
    def get_subpackage_names (self):
        return ['devel', '']
    def srcdir (self):
        return re.sub (r'src\.v', '-', target.AutoBuild.srcdir (self))
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                .replace ('--config-cache', '--cache-file=config.cache'))
    def update_libtool (self):
        self.system ('''
cd %(builddir)s && %(srcdir)s/ltconfig --srcdir %(srcdir)s %(srcdir)s/ltmain.sh %(target_architecture)s'''
              , locals ())
        target.AutoBuild.update_libtool (self)
    def license_files (self):
        return ['%(sourcefiledir)s/jpeg.license']
    def configure (self):
        self.update_config_guess_config_sub ()
        target.AutoBuild.configure (self)
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
        target.AutoBuild.update_libtool (self)

class Libjpeg__linux (Libjpeg):
    def compile (self):
        Libjpeg.compile (self)
        self.file_sub ([('^#define (HAVE_STDLIB_H) *', '''#ifdef \\1
#define \\1
#endif''')],
               '%(builddir)s/jconfig.h')

class Libjpeg__tools (tools.AutoBuild):
    source = Libjpeg.source
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        source._version = 'v6b'
    def _get_build_dependencies (self):
        return ['libtool']
    def srcdir (self):
        return re.sub (r'src\.v', '-', tools.AutoBuild.srcdir (self))
    def force_autoupdate (self):
        '''libtoolize: `configure.ac' does not exist'''
        return False
    def configure (self):
        self.update_config_guess_config_sub ()
        tools.AutoBuild.configure (self)
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
