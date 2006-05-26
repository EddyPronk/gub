
import download
import toolpackage


class Automake(toolpackage.ToolBuildSpecification):
    def __init__ (self, settings):
	toolpackage.ToolBuildSpecification.__init__ (self, settings)
	self.with (mirror=download.gnu,
		   version="1.9.6", format='bz2')
