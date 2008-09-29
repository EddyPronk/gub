import os

from gub import cross
from gub import mirrors

class Odcctools (cross.CrossToolsBuild):
    source = ('svn:http://iphone-dev.googlecode.com/svn/trunk/odcctools'
              '&revision=278'
    def __init__ (self, settings, source):
        cross.CrossToolsBuild.__init__ (self, settings, source)
        if 'x86_64-linux' in self.settings.build_architecture:
            # odcctools does not build with 64 bit compiler
            cross.setup_linux_x86 (self)

    def patch(self):
        cross.CrossToolsBuild.patch(self)
        self.apply_patch('odcctools-r211-word.patch')
    def get_build_dependencies (self):
        return ['darwin-sdk']
    def configure (self):
        cross.CrossToolsBuild.configure (self)
        ## remove LD64 support.
        self.file_sub ([('ld64','')], self.builddir () + '/Makefile')

