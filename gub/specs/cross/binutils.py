from gub import build
from gub import cross

class Binutils (cross.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/binutils/binutils-2.18.tar.bz2'
    patches = ['binutils-2.18-makeinfo-version.patch', 'binutils-2.18-werror.patch' ]
    def _get_build_dependencies (self):
        return ['tools::texinfo']
    def xconfigure_command (self):
        # --werror is broken
        return (cross.AutoBuild.configure_command (self)
                + misc.join_lines ('''
--disable-werror
'''))
    def makeflags (self):
        ##return 'toolexeclibdir=%(system_prefix)s/lib'
        ##binutils' makefile uses:
        ## MULTIOSDIR = `$(CC) $(LIBCFLAGS) -print-multi-os-directory`
        ## which differs on each system.
        ## so we MUST set it.
        return 'MULTIOSDIR=../../lib'
    def install_librestrict_stat_helpers (self):
        # librestrict stats PATH to find gnm and gstrip
        self.system ('''
cd %(install_prefix)s%(cross_dir)s/bin && ln %(toolchain_prefix)sas %(toolchain_prefix)sgas
cd %(install_prefix)s%(cross_dir)s/bin && ln %(toolchain_prefix)snm %(toolchain_prefix)sgnm
cd %(install_prefix)s%(cross_dir)s/bin && ln %(toolchain_prefix)sstrip %(toolchain_prefix)sgstrip
cd %(install_prefix)s%(cross_dir)s/%(target_architecture)s/bin && ln as gas
cd %(install_prefix)s%(cross_dir)s/%(target_architecture)s/bin && ln nm gnm
cd %(install_prefix)s%(cross_dir)s/%(target_architecture)s/bin && ln strip gstrip
''')
    def install (self):
        cross.AutoBuild.install (self)
        self.install_librestrict_stat_helpers ()
        '''
        On some systems [Fedora9], libiberty.a is provided by binutils
        *and* by gcc

        http://lists.gnu.org/archive/html/lilypond-devel/2008-11/msg00163.html
        http://lists.gnu.org/archive/html/lilypond-devel/2009-02/msg00118.html
        
        Not all systems make binutils compile libiberty.a, so we
        optionally remove it.
        '''
        self.system ('rm %(install_prefix)s%(cross_dir)s/lib/libiberty.a',
                     ignore_errors=True)

class Binutils__linux__ppc (Binutils):
    patches = Binutils.patches + ['binutils-2.18-werror-ppc.patch']

class Binutils__mingw (Binutils):
    def _get_build_dependencies (self):
        return Binutils._get_build_dependencies (self) + ['tools::libtool']
    def configure (self):
        Binutils.configure (self)
        # Configure all subpackages, makes
        # w32.libtool_fix_allow_undefined to find all libtool files
        self.system ('cd %(builddir)s && make %(makeflags)s configure-host configure-target')
        # Must ONLY do target stuff, otherwise cross executables cannot find their libraries
#        self.map_locate (lambda logger,file: build.libtool_update (logger, self.expand ('%(tools_prefix)s/bin/libtool'), file), '%(builddir)s', 'libtool')
        self.map_locate (lambda logger, file: build.libtool_update (logger, self.expand ('%(tools_prefix)s/bin/libtool'), file), '%(builddir)s/libiberty', 'libtool')
