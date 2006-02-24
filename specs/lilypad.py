import download
import targetpackage

class LilyPad (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version='0.0.7-1', mirror=download.lp, format='bz2',
			   depends=['mingw-runtime', 'w32api'])

	def makeflags (self):
		# FIXME: better fix Makefile
		return misc.join_lines ('''
ALL_OBJS='$(OBJS)'
WRC=/usr/bin/wrc
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
