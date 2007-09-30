from gub import targetpackage

class Bash (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_template (version='3.2',
                   mirror='ftp://ftp.cwru.edu/pub/bash/bash-3.2.tar.gz',
                   format='bz2')

    def get_build_dependencies (self):
        return ['libtool', 'gettext-devel']


class Bash__mingw (Bash):
    def __init__ (self, settings):
        Bash.__init__ (self, settings)
        self.with_template (version='2.05b-MSYS',
                            mirror='http://ufpr.dl.sourceforge.net/sourceforge/mingw/bash-2.05b-MSYS-src.tar.bz2',
                            format='bz2', strip_components=2)

    def patch (self):
        self.file_sub ([(r'test \$ac_cv_sys_tiocgwinsz_in_termios_h != yes',
                         r'test "$ac_cv_sys_tiocgwinsz_in_termios_h" != yes'),
                        ], '%(srcdir)s/configure')
    
    def config_cache_overrides (self, str):
        str += 'bash_cv_have_mbstate_t=yes\n'
        return str
 
