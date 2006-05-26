import download
import toolpackage

class Autoconf(toolpackage.ToolBuildSpecification):
    def __init__ (self, settings):
	toolpackage.ToolBuildSpecification.__init__ (self, settings)
	self.with (mirror=download.gnu,
		   version="2.59", format='bz2')
