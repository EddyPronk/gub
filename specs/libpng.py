import download
import targetpackage

class Libpng (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version='1.2.8', mirror=download.libpng,
			   depends=['zlib'])

	def name (self):
		return 'libpng'

	def patch (self):
		self.file_sub ([('(@INSTALL.*)@PKGCONFIGDIR@',
				 r'\1${DESTDIR}@PKGCONFIGDIR@')],
			       '%(srcdir)s/Makefile.in')
		self.file_sub ([('(@INSTALL.*)@PKGCONFIGDIR@',
				 r'\1${DESTDIR}@PKGCONFIGDIR@')],
			       '%(srcdir)s/Makefile.am')

	def configure (self):
		targetpackage.Target_package.configure (self)
		# # FIXME: libtool too old for cross compile
		self.update_libtool ()

	def compile_command (self):
		c = targetpackage.Target_package.compile_command (self)
		## need to call twice, first one triggers spurious Automake stuff.		
		return '(%s) || (%s)' % (c,c)
	
class Libpng__mingw (Libpng):
	def configure (self):
		# libtool will not build dll if -no-undefined flag is
		# not present
		self.file_sub ([('-version-info',
				 '-no-undefined -version-info')],
			   '%(srcdir)s/Makefile.am')
		self.autoupdate ()
		Libpng.configure (self)

# FIXME: handling libtool, libiconv, zlib dependencies smarter (adding
# for mingw/freebsd or removing for darwin) would allow dropping quite
# some __platform subclasses.
class Libpng__darwin (Libpng):
	def __init__ (self, settings):
		Libpng.__init__ (self, settings)
		self.with (version='1.2.8', mirror=download.libpng, depends=[])
