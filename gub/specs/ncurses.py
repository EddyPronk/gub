from gub import misc
from gub import target
from gub import tools

class Ncurses (target.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.5.tar.gz'
    patches = ['ncurses-5.5-mkhashsize.sh.patch']
    dependencies = [
#            'system::g++'
            'tools::ncurses',
            'tools::gawk',
            ]
    configure_flags = (target.AutoBuild.configure_flags
                + ' --without-normal'
                + ' --with-shared'
                )
    license_files = ['%(srcdir)s/README']

    if 'stat' in misc.librestrict ():
        def autoupdate (self):
            target.AutoBuild.autoupdate (self)
            # Cross ...WHAT?
            self.file_sub ([(' (/etc|/opt|/usr|/var)', r' %(system_prefix)s\1')],
                           '%(srcdir)s/configure')
        def LD_PRELOAD (self):
            return '%(tools_prefix)s/lib/librestrict-open.so'

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
    make_flags = 'SCRIPT_SHELL=/bin/bash'
    license_files = ['%(srcdir)s/README']
