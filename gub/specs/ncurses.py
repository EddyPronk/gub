from gub import targetpackage
from gub import mirrors

class Ncurses (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_template (mirror=mirrors.gnu, version='5.5')
    def license_file (self):
        return '%(srcdir)s/README'
