from gub import mirrors
from gub import targetbuild

class Libdbi (targetbuild.TargetBuild):
    def __init__ (self, settings):
        targetbuild.TargetBuild.__init__ (self, settings)
        self.with_template (version='0.8.1', mirror=mirrors.sf, format='gz')

    def patch (self):
        targetbuild.TargetBuild.patch (self)
        self.file_sub ([('SUBDIRS *=.*', 'SUBDIRS = src include')],
                       '%(srcdir)s/Makefile.in')

