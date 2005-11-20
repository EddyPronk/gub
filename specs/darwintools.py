import re
import gub

class  Darwin_sdk (gub.Package):
	def file_name (self):
		return 'darwin-sdk.tar.gz'
	def __init__ (self, settings):
		gub.Package.__init__ (self, settings)

	def name (self):
		return 'darwin-sdk'

	def unpack_destination (self):
		return self.settings.systemdir

	def download (self):
		pass

	def configure (self):
		pass

	def compile (self):
		pass

	def install (self):
		pass
	
class Odcc_tools (gub.Package):
	def __init__ (self, settings):
		gub.Package.__init__ (self, settings)
		self.url = 'http://www.opendarwin.org/downloads/odcctools-20051031.tar.bz2'

	def name (self):
		return "odcctools"

	def installdir (self):
		return self.settings.tooldir
	
	def configure_command (self):
		cmd = gub.Package.configure_command (self)
		cmd += ' --target=%s --with-sysroot=%s ' % (self.settings.target_architecture, self.settings.systemdir)
		
		return cmd

class Gcc (gub.Package):
	def __init__ (self, settings):
		gub.Package.__init__ (self,settings)
		self.url = 'ftp://dl.xs4all.nl/pub/mirror/gnu/gcc/gcc-4.0.2/gcc-4.0.2.tar.bz2'

	def patch (self):
		fn ='%s/gcc/config/darwin.h' % self.srcdir()
		str = open (fn).read ()

		# backup file.
		open (fn + "~", 'w').write (str)
		
		str = re.sub ('/usr/bin/libtool', '%s/bin/powerpc-apple-darwin-libtool' % self.settings.tooldir, str)
		open (fn,'w').write (str)
		
	def configure_command (self):
		cmd = gub.Package.configure_command (self)
		cmd += ''' --prefix=%(tooldir)s \
--program-prefix=%(target_architecture)s- \
--target=%(target_architecture)s \
--with-as=%(tooldir)s/bin/powerpc-apple-darwin-as  \
--with-ld=%(tooldir)s/bin/powerpc-apple-darwin-ld  \
--with-sysroot=%(systemdir)s --enable-static --enable-shared  \
--enable-languages=c ''' % self.settings.__dict__ # let's skip c++ for the moment.
		return cmd

		


def get_packages (settings):
	return [Darwin_sdk (settings),
		Odcc_tools (settings),
		Gcc (settings)]
		
	
