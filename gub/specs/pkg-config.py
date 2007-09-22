from gub import mirrors
from gub import toolpackage

class Pkg_config (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with_template (version="0.20",
                   mirror=mirrors.freedesktop),
    def get_build_dependencies (self):
        return ['libtool']
    def configure (self):
        toolpackage.ToolBuildSpec.configure (self)
        self.update_libtool ()
