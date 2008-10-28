from gub import misc
from gub import targetbuild

class LilyPad (targetbuild.AutoBuild):
    source = 'http://lilypond.org/download/gub-sources/lilypad-0.0.7-1-src.tar.bz2'
    def patch (self):
        ## windres doesn't handle --nostdinc
        self.file_sub ([('--nostdinc',' '),
                (r'rc\.res:', r'rc.res.o:')],
               "%(srcdir)s/Make.rules.in")
    def makeflags (self):
        # FIXME: better fix Makefile
        return misc.join_lines ('''
ALL_OBJS='$(OBJS)'
WRC=%(cross_prefix)s/bin/%(target_architecture)s-windres
CPPFLAGS=-I%(system_prefix)s/include
RC='$(WRC) $(CPPFLAGS)'
LIBWINE=
LIBPORT=
MKINSTALLDIRS=%(srcdir)s/mkinstalldirs
INSTALL_PROGRAM=%(srcdir)s/install-sh
''')
    def install_command (self):
        return targetbuild.AutoBuild.broken_install_command (self)
    def license_files (self):
        return ['']

Lilypad = LilyPad
