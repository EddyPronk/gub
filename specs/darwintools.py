import re
import gub
import download

class  Darwin_sdk (gub.Cross_package):
	def file_name (self):
		return 'darwin-sdk.tar.gz'

	def unpack_destination (self):
 		return self.settings.systemdir

	def configure (self):
		pass

	def compile (self):
		pass

	def install (self):
		pass
	
class Odcc_tools (gub.Cross_package):
	def installdir (self):
		return self.settings.tooldir
	

class Gcc (gub.Cross_package):
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
	sdk = Darwin_sdk (settings)
	sdk.url = 'http://lilypond.org/~hanwen/darwin-sdk.tar.gz'
	
	odc = Odcc_tools (settings)
	odc.url = 'http://www.opendarwin.org/downloads/odcctools-20051031.tar.bz2'
	
	gcc = Gcc (settings)

	download.set_gnu_download (gcc, '4.0.2', 'bz2')
	
	return [sdk, odc, gcc]
		
		
	
