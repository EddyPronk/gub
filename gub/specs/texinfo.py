from gub import mirrors
from gub import toolsbuild

class Texinfo__tools (toolsbuild.ToolsBuild):
    source = mirrors.with_template (name='texinfo', version="4.11",
                                    mirror=mirrors.gnu, format="bz2")
    def get_build_dependencies (self):
        return ['ncurses']
