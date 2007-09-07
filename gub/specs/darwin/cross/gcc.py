from gub.specs.cross import gcc
from gub import mirrors

class Gcc (gcc.Gcc):
    def __init__ (self, settings):
        #FIXME: separate-out: darwin-ppc/gcc.py / class Gcc__darwin__powerpc ()
        gcc.Gcc.__init__ (self, settings)
        if self.settings.target_architecture.startswith ("powerpc"):
            self.with_template (version='4.1.1', mirror=mirrors.gcc_41, format='bz2')
        else:
            self.with_template (version='4.2-20070207', mirror=mirrors.gcc_snap,
                       format='bz2')
    def patch (self):
        self.file_sub ([('/usr/bin/libtool', '%(cross_prefix)s/bin/%(target_architecture)s-libtool')],
                       '%(srcdir)s/gcc/config/darwin.h')

        self.file_sub ([('--strip-underscores', '--strip-underscore')],
                       "%(srcdir)s/libstdc++-v3/scripts/make_exports.pl")

    def configure_command (self):
        c = gcc.Gcc.configure_command (self)
#                c = re.sub ('enable-shared', 'disable-shared', c)
        return c
    

    def configure (self):
        gcc.Gcc.configure (self)

    def rewire_gcc_libs (self):
	import os
        skip_libs = ['libgcc_s']
        for ell in self.locate_files ("%(install_prefix)s/lib/", '*.dylib'):
            found_skips = [s for s in  skip_libs if ell.find (s) >= 0]
            if found_skips:
                continue
            
            id = self.read_pipe ('%(tool_prefix)sotool -L %(ell)s', 
		locals ()).split()[1]
            id = os.path.split (id)[1]
            self.system ('''
%(tool_prefix)sinstall_name_tool -id /usr/lib/%(id)s %(ell)s
''', locals ())
        
    def install (self):
        gcc.Gcc.install (self)
        self.rewire_gcc_libs ()

    def get_build_dependencies (self):
        return ['odcctools', 'cross/binutils']
    
class Not_used__Gcc__darwin (Gcc):
    def configure (self):
        gcc.Gcc.configure (self)

    def install (self):
        ## UGH ?
        ## Gcc.install (self)

        gcc.Gcc.install (self)
        self.rewire_gcc_libs ()
        
