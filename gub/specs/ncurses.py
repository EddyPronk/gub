from gub import target
from gub import tools

class Ncurses (target.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.5.tar.gz'
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ' --without-normal --with-shared ')
    def license_files (self):
        return ['%(srcdir)s/README']

class Ncurses__tools (tools.AutoBuild):
    source = Ncurses.source
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ' --with-normal --with-shared ')
    def license_files (self):
        return ['%(srcdir)s/README']
