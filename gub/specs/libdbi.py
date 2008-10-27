from gub import mirrors
from gub import targetbuild

class Libdbi (targetbuild.AutoBuild):
    source = mirrors.with_template (name='libdbi', version='0.8.1', mirror=mirrors.sf, format='gz')

    def patch (self):
        targetbuild.AutoBuild.patch (self)
        self.file_sub ([('SUBDIRS *=.*', 'SUBDIRS = src include')],
                       '%(srcdir)s/Makefile.in')

