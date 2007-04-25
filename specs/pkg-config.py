import mirrors
import toolpackage

class Pkg_config (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (version="0.20",
                   mirror=mirrors.freedesktop),

    def configure (self):
        toolpackage.ToolBuildSpec.configure (self)
        self.update_libtool ()
