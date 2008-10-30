from gub import target

class Libdbi (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/libdbi/libdbi-0.8.1.tar.gz'
    def patch (self):
        target.AutoBuild.patch (self)
        self.file_sub ([('SUBDIRS *=.*', 'SUBDIRS = src include')],
                       '%(srcdir)s/Makefile.in')

