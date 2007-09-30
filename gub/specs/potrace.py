from gub import toolsbuild

class Potrace (toolsbuild.ToolsBuild):
    def __init__ (self, settings):
        toolsbuild.ToolsBuild.__init__ (self, settings)
	from gub import mirrors
        self.with_template (mirror=mirrors.sf, version="1.7"),
