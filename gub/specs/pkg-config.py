from gub import tools

class Pkg_config__tools (tools.AutoBuild):
    dependencies = [
            'libtool',
            'system::g++',
            ]
