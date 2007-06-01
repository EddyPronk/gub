from gub import targetpackage
from gub import mirrors

class Psmisc (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_template (mirror=mirrors.sf, version='22.2')
    def get_build_dependencies (self):
        return ['ncurses']
