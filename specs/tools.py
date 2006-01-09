import re
import gub
import download
import misc
import os

class Tool_package (gub.Package):
	def configure_command (self):
		return (gub.Package.configure_command (self)
			+ misc.join_lines ('''
--prefix=%(tooldir)s/
'''))

	def install_command (self):
		return '''make DESTDIR=%(install_root)s prefix=/usr install'''

	def package (self):
		self.system ('''
tar -C %(install_root)s/ -zcf %(gub_uploads)s/%(gub_name)s .
''')

class Pkg_config (Tool_package):
	pass

class Guile (Tool_package):
	pass

class Gmp (Tool_package):
	pass

class Flex (Tool_package):
	def srcdir (self):
		return '%(allsrcdir)s/flex-2.5.4'

	def install_command (self):
		return self.broken_install_command ()
		
	def patch (self):
		self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/flex-2.5.4a-FC4.patch")


class Nsis (Tool_package):
	def compile (self): 
		env = {}
		env['PATH'] = '%(topdir)s/target/i686-mingw32/system/usr/cross/bin:' + os.environ['PATH']
		self.system ('cd %(builddir)s/ && make -C Source POSSIBLE_CROSS_PREFIXES=i686-mingw32- ', env)
			     
	def patch (self):
		self.system ("mkdir -p %(builddir)s", ignore_error=True) 
		self.system ('rm -rf %(builddir)s && ln -s %(srcdir)s %(builddir)s')
		
	def srcdir (self):
		d = Tool_package.srcdir (self).replace ('_','-')
		return d

	def configure (self):
		pass
	
	def install (self):
		self.system('''
cd %(builddir)s && ./install.sh %(system_root)s/usr/ %(install_root)s 
''')
# cd %(install_root)s/usr/ && mkdir bin && cd bin && ln -s ../share/NSIS/makensis .

	def package (self):
		self.system ('tar -C %(install_root)s/%(system_root)s/ -zcf %(gub_uploads)s/%(gub_name)s .')

class Scons (Tool_package):
	def compile (self):
		pass
	def patch (self):
		pass
	
	def configure (self):
		pass
	def install_command (self):
		return 'python %(srcdir)s/setup.py install --prefix=%(tooldir)s --root=%(install_root)s'
	def package (self):
		self.system ('tar -C %(install_root)s/%(tooldir)s/ -zcf %(gub_uploads)s/%(gub_name)s .')

class Alien (Tool_package):
	def srcdir (self):
		return '%(allsrcdir)s/alien'
	def patch (self):
		self.system ("mkdir -p %(builddir)s", ignore_error=True) 
		self.system ('rm -rf %(builddir)s && ln -s %(srcdir)s %(builddir)s')
	def configure (self):
		Tool_package.configure (self)
		self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/alien.patch')
	def configure_command (self):
		return 'perl Makefile.PL'

class Fakeroot (Tool_package):
	def srcdir (self):
		return re.sub ('_','-', Tool_package.srcdir(self))


def get_packages (settings):
	return [
		Nsis (settings).with (version='2.06',
				      mirror="http://ftp.debian.org/debian/pool/main/n/nsis/nsis_%(version)s.orig.tar.%(format)s",
				      
				      format="gz"),

		Scons (settings).with (version='0.96.91',
				       format = 'gz',
				       mirror=download.sf),
		Pkg_config (settings).with (version="0.20",
					    mirror=download.freedesktop),
		Guile (settings).with (version='1.6.7',
				       mirror=download.gnu, format='gz',
				       ),
		Flex (settings).with (version="2.5.4a",
				      mirror=download.nongnu, format='gz'),
		Alien (settings).with (version="8.60",
				       mirror="http://www.kitenet.net/programs/alien/alien_8.60.tar.gz",
				       format="gz"),

		Fakeroot(settings).with (version="1.2.10",
					 mirror="http://ftp.debian.org/debian/pool/main/f/fakeroot/fakeroot_1.2.10.tar.gz",
					 format="gz"),
	
					 
		]


def change_target_packages (bla):
	pass

