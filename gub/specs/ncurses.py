from gub import targetpackage
from gub import mirrors

class Ncurses (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_template (mirror=mirrors.gnu, version='5.5')
