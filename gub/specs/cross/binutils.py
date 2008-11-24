from gub import build
from gub import cross

class Binutils (cross.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/binutils/binutils-2.18.tar.bz2'
    patches = ['binutils-2.18-makeinfo-version.patch', 'binutils-2.18-werror.patch' ]
    def get_build_dependencies (self):
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
    def FIXME_breaks_on_some_linuxes_install (self):
        # please document why this should be removed?
        cross.AutoBuild.install (self)
        self.system ('rm %(install_prefix)s%(cross_dir)s/lib/libiberty.a')

class Binutils__linux__ppc (Binutils):
    source = Binutils.source
    patches = Binutils.patches + ['binutils-2.18-werror-ppc.patch']

class Binutils__mingw (Binutils):
    patches = Binutils.patches
    def get_build_dependencies (self):
        return Binutils.get_build_dependencies (self) + ['tools::libtool']
    def configure (self):
        Binutils.configure (self)
        # Configure all subpackages, makes
        # w32.libtool_fix_allow_undefined to find all libtool files
        self.system ('cd %(builddir)s && make %(makeflags)s configure-host configure-target')
        # Must ONLY do target stuff, otherwise cross executables cannot find their libraries
#        self.map_locate (lambda logger,file: build.libtool_update (logger, self.expand ('%(tools_prefix)s/bin/libtool'), file), '%(builddir)s', 'libtool')
        self.map_locate (lambda logger, file: build.libtool_update (logger, self.expand ('%(tools_prefix)s/bin/libtool'), file), '%(builddir)s/libiberty', 'libtool')
