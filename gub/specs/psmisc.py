from gub import targetbuild
from gub import mirrors

class Psmisc (targetbuild.TargetBuild):
    source = mirrors.with_template (name='psmisc', mirror=mirrors.sf, version='22.2')
    def get_subpackage_names (self):
        return ['']
    def get_build_dependencies (self):
        return ['ncurses']
