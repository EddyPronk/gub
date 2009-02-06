import re
#
from gub import target
from gub import tools

class Gmp (target.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/gmp/gmp-4.2.1.tar.gz'

    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        if not self.settings.platform.startswith ('darwin'):
            self.target_architecture = re.sub ('i[0-9]86-', 'i386-', settings.target_architecture)

    def get_build_dependencies (self):
        return ['libtool', 'tools::autoconf', 'tools::automake', 'tools::libtool']

    def configure_command (self):
        c = target.AutoBuild.configure_command (self)

        c += ' --disable-cxx '
        return c

    def configure (self):
        target.AutoBuild.configure (self)
        # automake's Makefile.in's too old for new libtool,
        # but autoupdating breaks even more.  This nice
        # hack seems to work.
        self.file_sub ([('#! /bin/sh', '#! /bin/sh\ntagname=CXX'),
                        ('#! /bin/bash', '#! /bin/bash\ntagname=CXX')],
               '%(builddir)s/libtool')
        
class Gmp__darwin (Gmp):
    def patch (self):

        ## powerpc/darwin cross barfs on all C++ includes from
        ## a C linkage file.
        ## don't know why. Let's patch C++ completely from GMP.

        self.file_sub ([('__GMP_DECLSPEC_XX std::[oi]stream& operator[<>][^;]+;$', ''),
                ('#include <iosfwd>', ''),
                ('<cstddef>','<stddef.h>')
                ],
               '%(srcdir)s/gmp-h.in')
        Gmp.patch (self)

    def install (self):
        Gmp.install (self)
        self.file_sub ([('using std::FILE;','')],
                       '%(install_prefix)s/include/gmp.h')

class Gmp__darwin__x86 (Gmp__darwin):
    def configure_command (self):

        ## bypass oddball assembler errors. 
        c = Gmp__darwin.configure_command (self)
        c = re.sub ('host=[^ ]+', 'host=none-apple-darwin8', c)
        c = re.sub ('--target=[^ ]+', ' ', c)
        return c

class Gmp__cygwin (Gmp):
    source = 'ftp://ftp.gnu.org/pub/gnu/gmp/gmp-4.1.4.tar.gz'
    patches = ['gmp-4.1.4-1.patch']

class Gmp__mingw (Gmp):
    patches = ['gmp-4.1.4-1.patch']
    def __init__ (self, settings, source):
        Gmp.__init__ (self, settings, source)
        # Configure (compile) without -mwindows for console
        self.target_gcc_flags = '-mms-bitfields'
        
    def install (self):
        Gmp.install (self)
        self.system ('''
mv %(install_prefix)s/lib/*dll %(install_prefix)s/bin || true
''')

class Gmp__freebsd (Gmp):
    source = 'ftp://ftp.gnu.org/pub/gnu/gmp/gmp-4.2.4.tar.gz'

class Gmp__tools (tools.AutoBuild, Gmp):
    source = Gmp.source
    def get_build_dependencies (self):
        return ['libtool']            
