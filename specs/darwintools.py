import glob
import re
import gub
import download

from gub import join_lines

class Darwin_sdk (gub.Binary_package):
	def file_name (self):
		return 'darwin-sdk.tar.gz'

	def patch (self):
		pat = self.settings.system_root + '/usr/lib/*.la'
		for a in glob.glob (pat):
			self.file_sub (r' (/usr/lib/.*\.la)', '%(system_root)s\1', a)

		
	
class Odcctools (gub.Cross_package):
	def install_prefix (self):
		return self.settings.tooldir
	
class Gcc (gub.Cross_package):
	def patch (self):
		fn ='%s/gcc/config/darwin.h' % self.srcdir ()
		self.file_sub ('/usr/bin/libtool', '%(tooldir)s/bin/powerpc-apple-darwin7-libtool',
			       fn)

	def configure_command (self):
		cmd = gub.Cross_package.configure_command (self)
		cmd += '''
--prefix=%(tooldir)s 
--program-prefix=%(target_architecture)s-
--with-as=%(tooldir)s/bin/powerpc-apple-darwin7-as  
--with-ld=%(tooldir)s/bin/powerpc-apple-darwin7-ld  
--enable-static
--enable-shared  
--enable-libstdcxx-debug 
--enable-languages=c,c++ ''' % self.settings.__dict__
		
		return join_lines (cmd)


def get_packages (settings):
	return (
		Darwin_sdk (settings).with (version='', mirror=download.hw),
		Odcctools (settings).with (version='20051031', mirror=download.opendarwin, format='bz2'),
		Gcc (settings).with (version='4.0.2', format='bz2'),
		)		
