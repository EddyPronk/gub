from toolpackage import Tool_package
import re

class Fontforge (Tool_package):
	def srcdir (self):
		return re.sub ('_full', '', Tool_package.srcdir(self))

	def install_command (self):
		return self.broken_install_command ()

	def configure_command (self):
		return Tool_package.configure_command (self) + " --without-freetype-src "
	def patch (self):
		Tool_package.patch (self)
		self.system ("cd %(srcdir)s && patch -p0 < %(patchdir)s/fontforge-20060501-srcdir.patch")
		
	def __init__ (self, settings):
		Tool_package.__init__ (self, settings)
		self.with (mirror="http://fontforge.sourceforge.net/fontforge_full-%(version)s.tar.bz2",
			   version="20060501"),
		
