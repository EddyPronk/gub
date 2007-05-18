from gub import toolpackage

class Potrace (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
	from gub import mirrors
        self.with_template (mirror=mirrors.sf, version="1.7"),
