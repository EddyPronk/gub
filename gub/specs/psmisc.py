from gub import target

class Psmisc (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/psmisc/psmisc-22.2.tar.gz'
    subpackage_names = ['']
    dependencies = ['ncurses']
