from gub import target

class Tslib (target.AutoBuild):
    source = 'http://download.berlios.de/tslib/tslib-1.0.bz2'
    def configure (self):
        target.AutoBuild.configure (self)
        self.file_sub ([('#define malloc', '#define urg_malloc')],
                       '%(builddir)s/config.h')
