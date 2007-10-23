import os

from gub import cross
from gub import mirrors

class Odcctools (cross.CrossToolsBuild):
    source = mirrors.with_template (name='odcctools', version='20060413',
                   ####version='20060608',
                   #version='20061117',
                   mirror=mirrors.opendarwin,
                   format='bz2')
    def __init__ (self, settings, source):
        cross.CrossToolsBuild.__init__ (self, settings, source)
    def get_build_dependencies (self):
        return ['darwin-sdk']
    def configure (self):
        cross.CrossToolsBuild.configure (self)
        ## remove LD64 support.
        self.file_sub ([('ld64','')], self.builddir () + '/Makefile')
    def compile (self): 
        self.system ('cd %(builddir)s && %(compile_command)s',
                     self.get_compile_env ())
    def get_compile_env (self):
        env = {'PATH': os.environ['PATH']}
        if 'x86_64-linux' in self.settings.build_architecture:
            # odcctools does not build with 64 bit compiler
            from gub import cross
            return cross.setup_linux_x86 (self, env)
        return env

