from gub import targetbuild
from gub import toolsbuild

class Ncurses (targetbuild.TargetBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.5.tar.gz'
    def license_files (self):
        return '%(srcdir)s/README'

class Ncurses__tools (toolsbuild.ToolsBuild):
    source = Ncurses.source
    def license_files (self):
        return '%(srcdir)s/README'

