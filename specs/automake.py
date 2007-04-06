
import download
import toolpackage


class Automake(toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
	toolpackage.ToolBuildSpec.__init__ (self, settings)
	self.with (mirror=download.gnu,
		   version="1.10", format='gz')
