from gub import cross
from gub import mirrors

class Gcc (cross.Gcc):
    def __init__ (self, settings):
        #FIXME: separate-out: darwin-ppc/gcc.py / class Gcc__darwin__powerpc ()
        cross.Gcc.__init__ (self, settings)
        if self.settings.target_architecture.startswith ("powerpc"):
            self.with (version='4.1.1', mirror=mirrors.gcc_41, format='bz2')
        else:
            self.with (version='4.2-20070207', mirror=mirrors.gcc_snap,
                       format='bz2')
    def patch (self):
        self.file_sub ([('/usr/bin/libtool', '%(cross_prefix)s/bin/%(target_architecture)s-libtool')],
                       '%(srcdir)s/gcc/config/darwin.h')

        self.file_sub ([('--strip-underscores', '--strip-underscore')],
                       "%(srcdir)s/libstdc++-v3/scripts/make_exports.pl")

    def configure_command (self):
        c = cross.Gcc.configure_command (self)
#                c = re.sub ('enable-shared', 'disable-shared', c)
        return c
    

    def configure (self):
        cross.Gcc.configure (self)

    def rewire_gcc_libs (self):
        skip_libs = ['libgcc_s']
        for l in self.locate_files ("%(install_root)s/usr/lib/", '*.dylib'):
            found_skips = [s for s in  skip_libs if l.find (s) >= 0]
            if found_skips:
                continue
            
            id = self.read_pipe ('%(tool_prefix)sotool -L %(l)s', locals ()).split()[1]
            id = os.path.split (id)[1]
            self.system ('%(tool_prefix)sinstall_name_tool -id /usr/lib/%(id)s %(l)s', locals ())
        
    def install (self):
        cross.Gcc.install (self)
        self.rewire_gcc_libs ()

    def get_build_dependencies (self):
        return ['odcctools', 'cross/binutils']
    
class Not_used__Gcc__darwin (Gcc):
    def configure (self):
        cross.Gcc.configure (self)

    def install (self):
        ## UGH ?
        ## Gcc.install (self)

        cross.Gcc.install (self)
        self.rewire_gcc_libs ()
        
