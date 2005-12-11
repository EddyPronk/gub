import download
import framework
import glob
import gub
import re

class Darwin_sdk (gub.Binary_package):
	def file_name (self):
		return 'darwin-sdk.tar.gz'

	def patch (self):
		pat = self.settings.system_root + '/usr/lib/*.la'
		for a in glob.glob (pat):
			self.file_sub ([(r' (/usr/lib/.*\.la)', r'%(system_root)s\1')], a)

	def install (self):

		# don't add usr/ to root.
		self.system ('mkdir -p %(install_root)s/')
		self.system ('tar -C %(srcdir)s/root -cf- . | tar -C %(install_root)s/ -xvf-')

	
	def sysinstall (self):
		self._install_gub (self.settings.system_root)

	def package (self):
		# naive tarball packages for now
		self.system ('''
tar -C %(install_root)s -zcf %(gub_uploads)s/%(gub_name)s .
''')

		
	
class Odcctools (gub.Cross_package):
	def install_prefix (self):
		return self.settings.tooldir

	def configure (self):
		gub.Cross_package.configure (self)

		## remove LD64 support.
		self.file_sub ([('ld64','')],
			       self.builddir () + '/Makefile')

#class Gcc (cross.Gcc):
class Gcc (framework.Gcc):
	def patch (self):
		self.file_sub ([('/usr/bin/libtool', '%(tooldir)s/bin/%(target_architecture)s-libtool')],
			       '%(srcdir)s/gcc/config/darwin.h')

	def install (self):
		gub.Cross_package.install (self)
		self.system ('''
(cd %(tooldir)s/lib && ln -s libgcc_s.1.dylib libgcc_s.dylib)
''')

def get_packages (settings):
	return (
		##  download.hw
		Darwin_sdk (settings).with (version='', mirror=lambda: 'http://lilypond.org/~hanwen/darwin-sdk.tar.gz'),
		
#		Odcctools (settings).with (version='20051031', mirror=download.opendarwin, format='bz2'),
		Odcctools (settings).with (version='20051122', mirror=download.opendarwin, format='bz2'),		
		Gcc (settings).with (version='4.0.2', format='bz2'),
		)		
