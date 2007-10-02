from gub import targetbuild
from gub import mirrors

class Ncurses (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        self.with_template (mirror=mirrors.gnu, version='5.5')
    def license_file (self):
        return '%(srcdir)s/README'
