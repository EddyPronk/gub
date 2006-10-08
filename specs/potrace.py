from toolpackage import ToolBuildSpec

class Potrace (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
	import download
        self.with (mirror=download.sf, version="1.7"),
