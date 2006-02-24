import download
import targetpackage

class Zlib (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version='1.2.2-1', mirror=download.lp, format='bz2')

	def patch (self):
		self.shadow_tree ('%(srcdir)s', '%(builddir)s')
		targetpackage.Target_package.patch (self)
		self.file_sub ([("='/bin/true'", "='true'")],
			       '%(srcdir)s/configure')
	def configure (self):
		zlib_is_broken = 'SHAREDTARGET=libz.so.1.2.2'
		if self.settings.platform.startswith ('mingw'):
			zlib_is_broken = 'target=mingw'
		self.system ('''
sed -i~ 's/mgwz/libz/' %(srcdir)s/configure
cd %(builddir)s && %(zlib_is_broken)s AR="%(AR)s r" %(srcdir)s/configure --shared
''', locals ())

	def install_command (self):
		return targetpackage.Target_package.broken_install_command (self)
