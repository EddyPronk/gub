from gub import mirrors
from gub import targetpackage
from gub import misc

class LilyPad (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_template (version='0.0.7-1',
                   mirror='http://lilypond.org/download/gub-sources/lilypad-0.0.7-1-src.tar.bz2',
                   format='bz2')

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

    def compile_command (self):
        return (targetpackage.TargetBuild.compile_command (self)
           + self.makeflags ())

    def install_command (self):
        return (targetpackage.TargetBuild.broken_install_command (self)
           + self.makeflags ())
    def license_file (self):
        return ''

Lilypad = LilyPad
