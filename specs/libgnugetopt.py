import download
import targetpackage

class Libgnugetopt (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='1.3', format='bz2', mirror=download.freebsd_ports)

    def patch (self):
        self.dump ('''
prefix = /usr
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

