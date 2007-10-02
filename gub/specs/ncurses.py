from gub import targetbuild
from gub import mirrors

class Ncurses (targetbuild.TargetBuild):
    source = mirrors.with_template (name='ncurses', mirror=mirrors.gnu, version='5.5')
    def license_file (self):
        return '%(srcdir)s/README'
