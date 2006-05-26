import download
import toolpackage

class Autoconf(toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
	toolpackage.ToolBuildSpec.__init__ (self, settings)
	self.with (mirror=download.gnu,
		   version="2.59", format='bz2')
