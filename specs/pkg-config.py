from toolpackage import ToolBuildSpecification
import download

class Pkg_config (ToolBuildSpecification):
    def __init__ (self, settings):
        ToolBuildSpecification.__init__ (self, settings)
        self.with (version="0.20",
             mirror=download.freedesktop),
