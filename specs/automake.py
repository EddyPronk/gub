
import download
import toolpackage


class Automake(toolpackage.Tool_package):
    def __init__ (self, settings):
	toolpackage.Tool_package.__init__ (self, settings)
	self.with (mirror=download.gnu,
		   version="1.9.6", format='bz2')
