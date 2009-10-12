from gub import build
from gub import cross
from gub import misc
from gub.specs import binutils

class Binutils (cross.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/binutils/binutils-2.19.1.tar.gz'
    patches = []
    dependencies = [
        'tools::zlib',
            ]
    # Block usage of libz.so during configure, which may not be
    # available in the library path.
    config_cache_overrides = cross.AutoBuild.config_cache_overrides + '''
ac_cv_search_zlibVersion=
'''
    configure_flags = (cross.AutoBuild.configure_flags
                       + ' --disable-werror'
                       + ' --cache-file=%(builddir)s/config.cache'
                       )
    configure_variables = (cross.AutoBuild.configure_variables
                           + misc.join_lines ('''
LDFLAGS='-L%(tools_prefix)s/lib %(rpath)s %(libs)s'
'''))
#CC='gcc -L%(tools_prefix)s/lib %(rpath)s %(libs)s'
#LD_LIBRARY_PATH=%(tools_prefix)s/lib
    # binutils' makefile uses:
    #     MULTIOSDIR = `$(CC) $(LIBCFLAGS) -print-multi-os-directory`
    # which differs on each system.  Setting it avoids inconsistencies.
    make_flags = misc.join_lines ('''
MULTIOSDIR=../../lib
''')
#CCLD='$(CC) -L%(tools_prefix)s/lib %(rpath)s'
    def install (self):
        cross.AutoBuild.install (self)
        binutils.install_missing_plain_binaries (self)
        binutils.install_librestrict_stat_helpers (self)
        binutils.remove_fedora9_untwanted_but_mysteriously_built_libiberies (self)

class Binutils__linux__ppc (Binutils):
    patches = Binutils.patches + [
        'binutils-2.18-werror-ppc.patch'
        ]

class Binutils__mingw (Binutils):
    dependencies = Binutils.dependencies + [
            'tools::libtool',
            ]
    def configure (self):
        Binutils.configure (self)
        # Configure all subpackages, makes
        # w32.libtool_fix_allow_undefined to find all libtool files
        self.system ('cd %(builddir)s && make %(compile_flags)s configure-host configure-target')
        # Must ONLY do target stuff, otherwise cross executables cannot find their libraries
#        self.map_locate (lambda logger,file: build.libtool_update (logger, self.expand ('%(tools_prefix)s/bin/libtool'), file), '%(builddir)s', 'libtool')
        self.map_locate (lambda logger, file: build.libtool_update (logger, self.expand ('%(tools_prefix)s/bin/libtool'), file), '%(builddir)s/libiberty', 'libtool')
