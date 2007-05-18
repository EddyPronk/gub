from gub import mirrors
from gub import toolpackage

class Autoconf(toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
	toolpackage.ToolBuildSpec.__init__ (self, settings)
	self.with_template (mirror=mirrors.gnu,
		   version="2.59", format='bz2')
