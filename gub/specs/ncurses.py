from gub import targetbuild
from gub import toolsbuild

class Ncurses (targetbuild.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.5.tar.gz'
    def license_files (self):
        return ['%(srcdir)s/README']

class Ncurses__tools (toolsbuild.AutoBuild):
    source = Ncurses.source
    def license_files (self):
        return ['%(srcdir)s/README']

