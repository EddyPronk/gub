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


class Mftrace (Tool_package):
	pass

class Potrace (Tool_package):
	pass

class Distcc (Tool_package):
	pass

class Fontforge (Tool_package):
	def srcdir (self):
		return re.sub ('_full', '', Tool_package.srcdir(self))

	def xpatch (self):
		Tool_package.patch (self)
		self.shadow_tree ('%(srcdir)s', '%(builddir)s')

	def install_command (self):
		return self.broken_install_command ()
		
class Guile (Tool_package):
	pass

class Flex (Tool_package):
	def srcdir (self):
		return '%(allsrcdir)s/flex-2.5.4'

	def install_command (self):
		return self.broken_install_command ()
		
	def patch (self):
		self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/flex-2.5.4a-FC4.patch")


## 2.06 and earlier.
class Nsis (Tool_package):
	def compile (self): 
		env = {}
		env['PATH'] = '%(topdir)s/target/mingw/system/usr/cross/bin:' + os.environ['PATH']
		self.system ('cd %(builddir)s/ && make -C Source POSSIBLE_CROSS_PREFIXES=i686-mingw32- ', env)
			     
	def patch (self):
		## Can't use symlinks for files, since we get broken symlinks in .gub
		self.system ('mkdir -p %(allbuilddir)s', ignore_error=True)
		self.system ('ln -s %(srcdir)s %(builddir)s') 
		
	def srcdir (self):
		d = Tool_package.srcdir (self).replace ('_','-')
		return d

	def configure (self):
		pass
	
	def install (self):
		## this is oddball, the installation ends up in system/usr/usr/
		## but it works ...
		self.system('''
cd %(builddir)s && ./install.sh %(system_root)s/usr/ %(install_root)s 
''')
# cd %(install_root)s/usr/ && mkdir bin && cd bin && ln -s ../share/NSIS/makensis .

	def package (self):
		self.system ('tar -C %(install_root)s/%(system_root)s/ -zcf %(gub_uploads)s/%(gub_name)s .')

class Nsis__scons (Tool_package):
	def patch (self):
		for f in ['SCons/Tools/crossmingw.py',
			  'Contrib/StartMenu/StartMenu.c',
			  'Source/7zip/LZMADecode.c',
			  'Source/build.cpp',
			  ]:
			self.file_sub (
				[('\r','')],
				'%(srcdir)s/' + f)
		self.system ("cd %(srcdir)s && patch -p0 < %(patchdir)s/nsis-2.14-mingw.patch")
		self.system ("cd %(srcdir)s && patch -p0 < %(patchdir)s/nsis-2.14-local.patch")
		self.system ('mkdir -p %(allbuilddir)s', ignore_error=True)
		self.system ('ln -s %(srcdir)s %(builddir)s') 
		
	def configure (self):
		pass
	
	def compile_command (self):

		## no trailing / in paths!
		return (' scons PREFIX=%(system_root)s/usr PREFIX_DEST=%(install_root)s '
			' DEBUG=yes '
			' SKIPPLUGINS=System')
	
	def compile (self): 
		env = {'PATH': '%(topdir)s/target/mingw/system/usr/cross/bin:' + os.environ['PATH']}
		self.system ('cd %(builddir)s/ && %(compile_command)s',
			     env)

	def install (self):
		env = {'PATH': '%(topdir)s/target/mingw/system/usr/cross/bin:' + os.environ['PATH']}
		self.system ('cd %(builddir)s/ && %(compile_command)s install ', env)

	def package (self):
		self.system ('tar -C %(install_root)s/%(system_root)s/ -zcf %(gub_uploads)s/%(gub_name)s .')

		
	def srcdir (self):
		d = Tool_package.srcdir (self).replace ('_','-')
		return d
		     


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
		self.shadow_tree ('%(srcdir)s', '%(builddir)s')

	def configure (self):
		Tool_package.configure (self)
		self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/alien.patch')
	def configure_command (self):
		return 'perl Makefile.PL'

class Fakeroot (Tool_package):
	def srcdir (self):
		return re.sub ('_','-', Tool_package.srcdir(self))


def get_packages (settings):
	ps = [
		Nsis__scons (settings).with (version='2.14',
				      mirror="http://ftp.debian.org/debian/pool/main/n/nsis/nsis_%(version)s.orig.tar.%(format)s",				      
				      
				      format="gz"),

		Scons (settings).with (version='0.96.91',
				       format = 'gz',
				       mirror=download.sf),
		Mftrace (settings).with (version='1.1.18',
					 mirror="http://www.xs4all.nl/~hanwen/mftrace/mftrace-1.1.18.tar.gz"),
		Distcc (settings).with (version='2.18.3',
					mirror="http://distcc.samba.org/ftp/distcc/distcc-%(version)s.tar.bz2"),
		

		Potrace (settings).with (mirror="http://potrace.sourceforge.net/download/potrace-%(version)s.tar.gz",
					 version="1.7"),
		Fontforge (settings).with (mirror="http://fontforge.sourceforge.net/fontforge_full-%(version)s.tar.bz2",
					 version="20060125"),
		
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

	return ps

def change_target_packages (bla):
	pass

