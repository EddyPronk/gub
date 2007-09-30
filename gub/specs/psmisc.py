from gub import targetbuild
from gub import mirrors

class Psmisc (targetbuild.TargetBuild):
    def __init__ (self, settings):
        targetbuild.TargetBuild.__init__ (self, settings)
        self.with_template (mirror=mirrors.sf, version='22.2')
    def get_subpackage_names (self):
        return ['']
    def get_build_dependencies (self):
        return ['ncurses']
