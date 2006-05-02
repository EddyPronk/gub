import download
import targetpackage

# Shared libraries do not build with Boost's home-grown build system
# [that hides compile and link commands].
class Boost (targetpackage.Target_package):
    def __init__ (self,settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='1.33.1', mirror=download.boost, format='bz2')

        # Configure generates invalid Makefile if CC has arguments
        self.target_gcc_flags = ''
        
    def patch (self):
        self.system ('''
cd %(srcdir)s/tools/build/v1 cp -pv gcc-tools.jam %(tool_prefix)sgcc.jam
''')
        self.file_sub ([
            (' ar ', ' %(tool_prefix)sar'),
            (' objcopy ', ' %(tool_prefix)sobjcopy'),
            ],
               '%(srcdir)s/tools/build/v1/gcc-tools.jam')
               
        # Boost does not support --srcdir builds
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')

    def get_substitution_dict (self, env={}):
        dict = targetpackage.Target_package.get_substitution_dict (self, env)
        # When using GCC, boost ignores standard CC,CXX
        # settings, but looks at GCC,GXX.
        dict['GCC'] = dict['CC']
        dict['GXX'] = dict['CXX']
        return dict

    def configure_command (self):
        # Boost configure barfs on standard options
###--with-toolset=%(tool_prefix)sgcc
        return misc.join_lines ('''C_INCLUDE_PATH= LIBRARY_PATH= %(srcdir)s/configure
--prefix=/usr
--includedir=/usr/include
--libdir=/usr/lib
--with-libraries=test
''')

    def install_command (self):
        return misc.join_lines ('''make install
EPREFIX=%(install_prefix)s
PREFIX=%(install_prefix)s
LIBDIR=%(install_prefix)s/lib
INCLUDEDIR=%(install_prefix)s/include
''')

    def install (self):
        targetpackage.Target_package.install (self)
        self.system ('''
cd %(install_prefix)s/include && mv boost-1_33_1/boost .
cd %(install_prefix)s/include && rm -rf boost-1_33_1
''')

class Boost__mingw (Boost):
    def patch (self):
        Boost.patch (self)
        self.file_sub ([
            ('-fPIC', ''),
            (' rt ', ' '),
            ('-pthread', '-mthreads'),
            ('"\$\(DLL_LINK_FLAGS\)"',
            '\1 "-Wl,--export-all-symbols"'),
            ],
               '%(srcdir)s/tools/build/v1/gcc-tools.jam')

    # HUH?
    def get_substitution_dict (self, env={}):
        return Boost.get_substitution_dict (self, env)

