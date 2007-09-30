from gub import mirrors
from gub import targetpackage

class Libgnugetopt (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_template (version='1.3', format='bz2', mirror=mirrors.freebsd_ports)

    def patch (self):
        self.dump ('''
prefix = %(prefix_dir)s
libdir = $(prefix)/lib
includedir = $(prefix)/include
install: all
\tinstall -d $(DESTDIR)/$(libdir)/
\tinstall -m 644 libgnugetopt.so.1 $(DESTDIR)/$(libdir)/
\tinstall -d $(DESTDIR)/$(includedir)/
\tinstall -m 644 getopt.h $(DESTDIR)/$(includedir)/
''',
             '%(srcdir)s/Makefile', mode='a')

    def configure (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')

    def license_file (self):

        ## is (L)GPL, but doesn't distribute license file.
        return '' 
