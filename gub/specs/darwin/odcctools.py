from gub import cross

class Odcctools (cross.AutoBuild):
    source = ('svn:http://iphone-dev.googlecode.com/svn&branch=trunk'
              '&module=odcctools'
              '&revision=278')
    def __init__ (self, settings, source):
        cross.AutoBuild.__init__ (self, settings, source)
        if 'x86_64-linux' in self.settings.build_architecture:
            # odcctools does not build with 64 bit compiler
            cross.change_target_package_x86 (self)
    def patch(self):
        cross.AutoBuild.patch(self)
        self.apply_patch('odcctools-r211-word.patch')
    def get_build_dependencies (self):
        return ['darwin-sdk']
    def configure (self):
        cross.AutoBuild.configure (self)
        ## remove LD64 support.
        self.file_sub ([('ld64','')], self.builddir () + '/Makefile')

