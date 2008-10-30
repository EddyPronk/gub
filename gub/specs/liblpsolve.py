from gub import misc
from gub import target

class Liblpsolve (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/lpsolve/lp_solve_5.5.0.13_source.tar.gz'
    def force_sequential_build (self):
        return True
    def get_build_dependencies (self):
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
    #FIXME: promoteme to build.py copies in python.py and lpsolve.py
#&& %(toolchain_prefix)snm bin/lib%(libname)s.dll | grep ' T _' | sed -e 's/.* T _//' -e 's/@.*//' | grep -Ev '^(atexit|_onexit)$' >> lib/lib%(libname)s.a.def
# && %(toolchain_prefix)snm bin/lib%(libname)s.dll | grep ' T _' | sed -e 's/.* T _//' | grep -Ev '^(atexit|_onexit)$' >> lib/lib%(libname)s.a.def
    def generate_dll_a_and_la (self, libname, depend=''):
        # ugh, atexit, _onexit mutliply defined in crt2.o
        self.system (misc.join_lines ('''
cd %(install_prefix)s
&& echo EXPORTS > lib/lib%(libname)s.a.def
&& %(toolchain_prefix)snm bin/lib%(libname)s.dll | grep ' T _' | sed -e 's/.* T _//' | grep -Ev '^(atexit|_onexit)$' >> lib/lib%(libname)s.a.def
&& (grep '@' lib/lib%(libname)s.a.def | sed -e 's/@.*//' >> lib/lib%(libname)s.a.def || :)
&& %(toolchain_prefix)sdlltool --def lib/lib%(libname)s.a.def --dllname bin/lib%(libname)s.dll --output-lib lib/lib%(libname)s.dll.a
'''), locals ())
        self.file_sub ([('LIBRARY', '%(libname)s'),
                        ('STATICLIB', ''),
                        ('DEPEND', ' %(depend)s'),
                        ('LIBDIR', '%(prefix_dir)s/lib')],
                       '%(sourcefiledir)s/libtool.la',
                       '%(install_prefix)s/lib/lib%(libname)s.la', env=locals ())
    def install (self):
        Liblpsolve.install (self)
        self.system ('mkdir -p %(install_prefix)s/bin')
        self.system ('mv %(install_prefix)s/lib/liblpsolve55.so %(install_prefix)s/bin/liblpsolve55.dll')
        self.generate_dll_a_and_la ('lpsolve55')

