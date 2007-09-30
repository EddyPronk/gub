from gub import toolsbuild

class Pkg_config (toolsbuild.ToolsBuild):
    def get_build_dependencies (self):
        return ['libtool']
    def configure (self):
        toolsbuild.ToolsBuild.configure (self)
        self.update_libtool ()
