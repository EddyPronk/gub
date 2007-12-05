from gub import mirrors
from gub import toolsbuild

class Autoconf (toolsbuild.ToolsBuild):
    def __init__ (self, settings, source):
	toolsbuild.ToolsBuild.__init__ (self, settings, source)
    source = mirrors.with_template (name='autoconf', mirror=mirrors.gnu,
		   version="2.59", format='bz2')
