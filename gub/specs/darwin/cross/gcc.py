import os

from gub.specs.cross import gcc
from gub import mirrors
from gub import loggedos

class Gcc (gcc.Gcc):
    source = mirrors.with_template (version='4.1.1', mirror=mirrors.gcc_41, format='bz2')
    def patch (self):
        self.file_sub ([('/usr/bin/libtool', '%(cross_prefix)s/bin/%(target_architecture)s-libtool')],
                       '%(srcdir)s/gcc/config/darwin.h')

        self.file_sub ([('--strip-underscores', '--strip-underscore')],
                       "%(srcdir)s/libstdc++-v3/scripts/make_exports.pl")
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
                                                 locals ())).split ()[1]
            id = os.path.split (id)[1]
            loggedos.system (
                logger, 
                self.expand ('%(toolchain_prefix)sinstall_name_tool -id /usr/lib/%(id)s %(file)s',
                             locals ()))

        self.map_locate (rewire_one,
                         self.expand ("%(install_prefix)s/lib/"),
                         '*.dylib')
        
    def install (self):
        gcc.Gcc.install (self)
        self.rewire_gcc_libs ()

    def get_build_dependencies (self):
        return ['odcctools', 'cross/binutils']
    
class Gcc__darwin__x86 (Gcc):
    source = mirrors.with_template (version='4.2.3', mirror=mirrors.gcc_snap, format='bz2')

class Not_used__Gcc__darwin (Gcc):
    def configure (self):
        gcc.Gcc.configure (self)

    def install (self):
        ## UGH ?
        ## Gcc.install (self)

        gcc.Gcc.install (self)
        self.rewire_gcc_libs ()
        
