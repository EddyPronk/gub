import download
import toolpackage

class Autoconf(toolpackage.Tool_package):
    def __init__ (self, settings):
	toolpackage.Tool_package.__init__ (self, settings)
	self.with (mirror=download.gnu,
		   version="2.59", format='bz2')
