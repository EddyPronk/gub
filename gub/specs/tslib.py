from gub import targetbuild

class Tslib (targetbuild.AutoBuild):
    source = 'http://download.berlios.de/tslib/tslib-1.0.bz2'
    def configure (self):
        targetbuild.AutoBuild.configure (self)
        self.file_sub ([('#define malloc', '#define urg_malloc')],
                       '%(builddir)s/config.h')
