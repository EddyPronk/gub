from gub import target

class Psmisc (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/psmisc/psmisc-22.2.tar.gz'
    def get_subpackage_names (self):
        return ['']
    def get_build_dependencies (self):
        return ['ncurses']
