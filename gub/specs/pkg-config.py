from gub import tools

class Pkg_config__tools (tools.AutoBuild):
    def _get_build_dependencies (self):
        return ['libtool']
