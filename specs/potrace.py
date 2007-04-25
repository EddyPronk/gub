import toolpackage

class Potrace (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
	import mirrors
        self.with (mirror=mirrors.sf, version="1.7"),
