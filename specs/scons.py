from toolpackage import Tool_package
import download

class Scons (Tool_package):
	def compile (self):
		pass

	def patch (self):
		pass
	
	def configure (self):
		self.system ('mkdir %(builddir)s')
	
	def install_command (self):
		return 'python %(srcdir)s/setup.py install --prefix=%(buildtools)s --root=%(install_root)s'

	def package (self):
		self.system ('tar -C %(install_root)s/%(buildtools)s/../ -zcf %(gub_uploads)s/%(gub_name)s .')
		self.dump_header_file()
	
	def __init__ (self, settings):
		Tool_package.__init__ (self, settings)
		self.with (version='0.96.91',
			   format = 'gz',
			   mirror=download.sf),
		
