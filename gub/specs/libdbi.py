from gub import mirrors
from gub import targetpackage

class Libdbi (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_template (version='0.8.1', mirror=mirrors.sf, format='gz')

    def patch (self):
        targetpackage.TargetBuildSpec.patch (self)
        self.file_sub ([('SUBDIRS *=.*', 'SUBDIRS = src include')],
                       '%(srcdir)s/Makefile.in')

