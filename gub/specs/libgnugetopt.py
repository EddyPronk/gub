from gub import target

class Libgnugetopt (target.MakeBuild):
    source = 'ftp://ftp.uk.freebsd.org/pub/FreeBSD/ports/local-distfiles/lioux/libgnugetopt-1.3.tar.bz2'
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
    def license_files (self):
        ## is (L)GPL, but doesn't distribute license file.
        return ['']
