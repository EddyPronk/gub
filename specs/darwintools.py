import re
import gub

class  Darwin_sdk (gub.Cross_package):
	def file_name (self):
		return 'darwin-sdk.tar.gz'
	def __init__ (self, settings, version):
		gub.Package.__init__ (self, settings, version)
		self.url = 'http://lilypond.org/~hanwen/darwin-sdk.tar.gz'
		
	def unpack_destination (self):
 		return self.settings.systemdir

	def configure (self):
		pass

	def compile (self):
		pass

	def install (self):
		pass
	
class Odcc_tools (gub.Cross_package):
	def __init__ (self, settings, version):
		gub.Cross_package.__init__ (self, settings, version)
		self.url = 'http://www.opendarwin.org/downloads/odcctools-20051031.tar.bz2'
	def installdir (self):
		return self.settings.tooldir
	

class Gcc (gub.Cross_package):
	def __init__ (self, settings, version):
		gub.Cross_package.__init__ (self,settings, version)
		self.url = 'ftp://dl.xs4all.nl/pub/mirror/gnu/gcc/gcc-4.0.2/gcc-4.0.2.tar.bz2'

	def patch (self):
		fn ='%s/gcc/config/darwin.h' % self.srcdir()
		str = open (fn).read ()

		# backup file.
		open (fn + "~", 'w').write (str)
		
		str = re.sub ('/usr/bin/libtool', '%s/bin/powerpc-apple-darwin7-libtool' % self.settings.tooldir, str)
		open (fn,'w').write (str)
		
	def configure_command (self):
		cmd = gub.Cross_package.configure_command (self)
		cmd += ''' --prefix=%(tooldir)s \
--program-prefix=%(target_architecture)s- \
--with-as=%(tooldir)s/bin/powerpc-apple-darwin7-as  \
--with-ld=%(tooldir)s/bin/powerpc-apple-darwin7-ld  \
 --enable-static --enable-shared  \
--enable-libstdcxx-debug \
--enable-languages=c,c++ ''' % self.settings.__dict__
		return cmd

		


def get_packages (settings):
	return [Darwin_sdk (settings, ''),
		Odcc_tools (settings, ''),
		Gcc (settings, '')]
		
	
