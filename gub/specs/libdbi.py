from gub import mirrors
from gub import targetpackage

class Libdbi (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_template (version='0.8.1', mirror=mirrors.sf, format='gz')

    def patch (self):
        targetpackage.TargetBuild.patch (self)
        self.file_sub ([('SUBDIRS *=.*', 'SUBDIRS = src include')],
                       '%(srcdir)s/Makefile.in')

