from gub import misc
from gub import target

class Liblpsolve (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/lpsolve/lp_solve_5.5.0.13_source.tar.gz'
    def force_sequential_build (self):
        return True
    def _get_build_dependencies (self):
        return ['tools::automake']
    def autoupdate (self):
        # install install-sh
        self.system ('cd %(srcdir)s && automake --add-missing --copy --force --foreign || :')
        self.shadow ()
    def makeflags (self):
        return misc.join_lines ('''
AR=%(toolchain_prefix)sar
LIBS=
RANLIB=%(toolchain_prefix)sranlib
''')
    def install_command (self):
        return self.broken_install_command ().replace ('includedir=%(install_prefix)s/include', 'includedir=%(install_prefix)s/include/lpsolve') 

class Liblpsolve__mingw (Liblpsolve):
    patches = ['lpsolve-5.5.0.13-mingw.patch']
    def install (self):
        Liblpsolve.install (self)
        self.system ('mkdir -p %(install_prefix)s/bin')
        self.system ('mv %(install_prefix)s/lib/liblpsolve55.so %(install_prefix)s/bin/liblpsolve55.dll')
        self.generate_dll_a_and_la ('lpsolve55')

