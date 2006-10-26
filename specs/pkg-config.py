from toolpackage import ToolBuildSpec
import download

class Pkg_config (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.with (version="0.20",
                   mirror=download.freedesktop),
