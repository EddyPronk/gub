from gub import mirrors
from gub import toolsbuild

class Autoconf(toolsbuild.ToolsBuild):
    def __init__ (self, settings, source):
	toolsbuild.ToolsBuild.__init__ (self, settings, source)
	self.with_template (mirror=mirrors.gnu,
		   version="2.59", format='bz2')
