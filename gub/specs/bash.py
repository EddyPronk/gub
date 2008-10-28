from gub import targetbuild

class Bash (targetbuild.AutoBuild):
    source = 'ftp://ftp.cwru.edu/pub/bash/bash-3.2.tar.gz'
    def get_build_dependencies (self):
        return ['libtool', 'gettext-devel']

class Bash__mingw (Bash):
    source = 'http://ufpr.dl.sourceforge.net/sourceforge/mingw/bash-2.05b-MSYS-src.tar.bz2&strip=2'
    def patch (self):
        self.file_sub ([(r'test \$ac_cv_sys_tiocgwinsz_in_termios_h != yes',
                         r'test "$ac_cv_sys_tiocgwinsz_in_termios_h" != yes'),
                        ], '%(srcdir)s/configure')
    def config_cache_overrides (self, str):
        str += 'bash_cv_have_mbstate_t=yes\n'
        return str
 
