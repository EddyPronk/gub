import download
import targetpackage
import misc

class LilyPad (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='0.0.7-1',
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
CPPFLAGS=-I%(system_root)s/usr/include
RC='$(WRC) $(CPPFLAGS)'
LIBWINE=
LIBPORT=
MKINSTALLDIRS=%(srcdir)s/mkinstalldirs
INSTALL_PROGRAM=%(srcdir)s/install-sh
''')

    def compile_command (self):
        return (targetpackage.TargetBuildSpec.compile_command (self)
           + self.makeflags ())

    def install_command (self):
        return (targetpackage.TargetBuildSpec.broken_install_command (self)
           + self.makeflags ())
    def license_file (self):
        return ''

Lilypad = LilyPad
