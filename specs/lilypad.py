import download
import targetpackage
import misc

class LilyPad (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='0.0.7-1',
                   mirror='http://lilypond.org/~hanwen/lilypad-0.0.7-1-src.tar.bz2',
                   format='bz2',

                   ## ugh, necessary?  
                   depends=['mingw-runtime', 'w32api'])

    def patch (self):
        ## windres doesn't handle --nostdinc
        self.file_sub ([('--nostdinc',' '),
                (r'rc\.res:', r'rc.res.o:')],
               "%(srcdir)s/Make.rules.in")
    def makeflags (self):
        # FIXME: better fix Makefile
        return misc.join_lines ('''
ALL_OBJS='$(OBJS)'
WRC=%(crossprefix)s/bin/%(target_architecture)s-windres
CPPFLAGS=-I%(system_root)s/usr/include
RC='$(WRC) $(CPPFLAGS)'
LIBWINE=
LIBPORT=
MKINSTALLDIRS=%(srcdir)s/mkinstalldirs
INSTALL_PROGRAM=%(srcdir)s/install-sh
''')

    def compile_command (self):
        return (targetpackage.Target_package.compile_command (self)
           + self.makeflags ())

    def install_command (self):
        return (targetpackage.Target_package.broken_install_command (self)
           + self.makeflags ())


Lilypad = LilyPad
