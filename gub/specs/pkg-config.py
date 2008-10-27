from gub import toolsbuild

class Pkg_config__tools (toolsbuild.AutoBuild):
    def get_build_dependencies (self):
        return ['libtool']
    def configure (self):
        toolsbuild.AutoBuild.configure (self)
        self.update_libtool ()
