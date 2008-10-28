import os
#
from gub.specs.cross import gcc
from gub import loggedos

class Gcc (gcc.Gcc):
    source = 'ftp://ftp.fu-berlin.de/unix/languages/gcc/releases/gcc-4.1.1/gcc-4.1.1.tar.bz2'
    def patch (self):
        self.file_sub ([('/usr/bin/libtool', '%(cross_prefix)s/bin/%(target_architecture)s-libtool')],
                       '%(srcdir)s/gcc/config/darwin.h')

        self.file_sub ([('--strip-underscores', '--strip-underscore')],
                       '%(srcdir)s/libstdc++-v3/scripts/make_exports.pl')
    def configure (self):
        gcc.Gcc.configure (self)
    def rewire_gcc_libs (self):
        skip_libs = ['libgcc_s']

        def rewire_one (logger, file):
            found_skips = [s for s in skip_libs if file.find (s) >= 0]
            if found_skips:
                return
            id = loggedos.read_pipe (logger,
                                     self.expand ('%(toolchain_prefix)sotool -L %(file)s', 
                                                 locals ()),
                                     env=self.get_substitution_dict ()).split ()[1]
            id = os.path.split (id)[1]
            loggedos.system (logger, 
                             self.expand ('%(toolchain_prefix)sinstall_name_tool -id /usr/lib/%(id)s %(file)s',
                                          locals ()),
                             env=self.get_substitution_dict ())
        self.map_locate (rewire_one,
                         self.expand ('%(install_prefix)s/lib/'),
                         '*.dylib')
    def install (self):
        gcc.Gcc.install (self)
        self.rewire_gcc_libs ()
    def get_build_dependencies (self):
        return ['odcctools', 'cross/binutils']
    
class Gcc__darwin__x86 (Gcc):
    source = 'ftp://ftp.fu-berlin.de/unix/languages/gcc/releases/gcc-4.3.2/gcc-4.3.2.tar.bz2'
    def get_build_dependencies (self):
        return ['tools::mpfr']

class Not_used__Gcc__darwin (Gcc):
    def configure (self):
        gcc.Gcc.configure (self)
    def install (self):
        gcc.Gcc.install (self)
        self.rewire_gcc_libs ()
        
