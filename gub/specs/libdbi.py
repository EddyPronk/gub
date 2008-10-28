from gub import targetbuild

class Libdbi (targetbuild.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/libdbi/libdbi-0.8.1.tar.gz'
    def patch (self):
        targetbuild.AutoBuild.patch (self)
        self.file_sub ([('SUBDIRS *=.*', 'SUBDIRS = src include')],
                       '%(srcdir)s/Makefile.in')

