from gub import context
from gub import target
from gub import tools

class Bash (target.AutoBuild):
    source = 'ftp://ftp.cwru.edu/pub/bash/bash-3.2.tar.gz'
    dependencies = ['libtool', 'gettext-devel']

class Bash__mingw (Bash):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/bash-2.05b-MSYS-src.tar.bz2&strip=2'
    def patch (self):
        self.file_sub ([(r'test \$ac_cv_sys_tiocgwinsz_in_termios_h != yes',
                         r'test "$ac_cv_sys_tiocgwinsz_in_termios_h" != yes'),
                        ], '%(srcdir)s/configure')
    config_cache_overrides = Bash.config_cache_overrides + '''
bash_cv_have_mbstate_t=yes
'''
 
no_patch = True # let's not use patch in a bootstrap package
class Bash__tools (tools.AutoBuild, Bash):
    patches = ['bash-3.2-librestrict.patch']
    parallel_build_broken = True
    if no_patch:
        patches = []
    def patch (self):
        if no_patch:
            self.file_sub ([('^  (check_dev_tty [(][)];)', r'  /* \1 */')],
                           '%(srcdir)s/shell.c')
        else:
            tools.AutoBuild.patch (self)
    def install (self):
        tools.AutoBuild.install (self)
        self.system ('cd %(install_prefix)s/bin && ln -s bash sh')
