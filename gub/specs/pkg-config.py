from gub import mirrors
from gub import toolsbuild

class Pkg_config (toolsbuild.ToolsBuild):
    def __init__ (self, settings):
        toolsbuild.ToolsBuild.__init__ (self, settings)
        self.with_template (version="0.20",
                   mirror=mirrors.freedesktop),
    def get_build_dependencies (self):
        return ['libtool']
    def configure (self):
        toolsbuild.ToolsBuild.configure (self)
        self.update_libtool ()
