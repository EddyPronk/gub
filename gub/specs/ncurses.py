from gub import target
from gub import tools

class Ncurses (target.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.5.tar.gz'
    patches = ['ncurses-5.5-mkhashsize.sh.patch']
    dependencies = [
#            'system::g++'
            'tools::gawk',
            ]
    configure_flags = (target.AutoBuild.configure_flags
                + ' --without-normal'
                + ' --with-shared'
                )
    def license_files (self):
        return ['%(srcdir)s/README']

class Ncurses__tools (tools.AutoBuild, Ncurses):
    patches = Ncurses.patches
    configure_flags = (tools.AutoBuild.configure_flags
                + ' --with-normal'
                + ' --with-shared'
                + ' --without-cxx'
                + ' --without--cxx-binding'
                )
    dependencies = [
#            'system::g++'
            'gawk',
            ]
    def makeflags (self):
        return 'SCRIPT_SHELL=/bin/bash'
    def license_files (self):
        return ['%(srcdir)s/README']
