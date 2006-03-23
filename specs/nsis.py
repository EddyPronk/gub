from toolpackage import Tool_package
import os

## 2.06 and earlier.
class Nsis__old (Tool_package):
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


class Nsis (Tool_package):
	def __init__ (self, settings):
		Tool_package.__init__(self, settings)
		self.with (
			version='2.15',
			#version='2.14',
			mirror="http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s-src.tar.%(format)s",
			
			format="bz2",
			depends=["scons"])

	def patch (self):
		if 0:  #2.14 patches
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

		if 1: #2.15 patches
			self.system ("cd %(srcdir)s && patch -p0 < %(patchdir)s/nsis-2.15-patchgenerator.patch")
			self.system ("cd %(srcdir)s && patch -p0 < %(patchdir)s/nsis-2.15-expand.patch")
		self.system ('mkdir -p %(allbuilddir)s', ignore_error=True)
		self.system ('ln -s %(srcdir)s %(builddir)s') 
		
	def configure (self):
		pass
	
	def compile_command (self):

		## no trailing / in paths!
		return (' scons PREFIX=%(system_root)s/usr PREFIX_DEST=%(install_root)s '
			' DEBUG=yes '

			## /s switch doesn't work anymore?!
			# ' NSIS_CONFIG_LOG=yes '
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
		d = Tool_package.srcdir (self).replace ('_','-') + '-src'
		return d
		     


