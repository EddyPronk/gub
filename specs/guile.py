import re
import os
#
import download
import misc
import targetpackage
import repository

from toolpackage import ToolBuildSpec


class Guile (targetpackage.TargetBuildSpec):
    def set_mirror(self):
        source = 'git://repo.or.cz/guile.git'
        repo = repository.Git (self.get_repodir (),
                               branch='branch_release-1-8', 
                               source=source)
        repo.version = lambda: '1.8.2'
        self.with_vc (repo)
        self.so_version = '17'

    def autogen_sh (self):
        self.file_sub ([(r'AC_CONFIG_SUBDIRS\(guile-readline\)', '')],
                       '%(srcdir)s/configure.in')
        self.file_sub ([(r'guile-readline', '')],
                       '%(srcdir)s/Makefile.am')
        self.dump ('',
                   '%(srcdir)s/doc/ref/version.texi')
        self.dump ('',
                   '%(srcdir)s/doc/tutorial/version.texi')
        
    def license_file (self):
        return '%(srcdir)s/COPYING.LIB' 
 
    def get_subpackage_names (self):
        return ['doc', 'devel', 'runtime', '']

    def get_dependency_dict (self):
        return {
            '' : ['guile-runtime'],
            'runtime': ['gmp', 'gettext', 'libtool-runtime'],
            'devel': ['guile-runtime'],
            'doc': ['texinfo'],
            }

    def get_build_dependencies (self):
        return ['gettext-devel', 'gmp-devel', 'libtool']
        
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.set_mirror ()

    # FIXME: C&P.
    def guile_version (self):
        return '.'.join (self.ball_version.split ('.')[0:2])

    def patch (self):
        self.autogen_sh()

        ## Don't apply patch twice.
        if None == re.search ('reloc_p=', open (self.expand ('%(srcdir)s/configure.in')).read()):
            self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/guile-reloc.patch')
            self.dump ('''#!/bin/sh
exec %(local_prefix)s/bin/guile "$@"
''', "%(srcdir)s/pre-inst-guile.in")
            
        self.autoupdate ()

    def configure_flags (self):
        return misc.join_lines ('''
--without-threads
--with-gnu-ld
--enable-deprecated
--enable-discouraged
--disable-error-on-warning
--enable-relocation
--disable-rpath
''')
        
    def configure_command (self):
        return ('GUILE_FOR_BUILD=%(local_prefix)s/bin/guile '
                + targetpackage.TargetBuildSpec.configure_command (self)
                + self.configure_flags ())

    def compile_command (self):
        return ('preinstguile=%(local_prefix)s/bin/guile ' +
                targetpackage.TargetBuildSpec.compile_command (self))
    
    def compile (self):

        ## Ugh : broken dependencies barf with make -jX
        self.system ('cd %(builddir)s/libguile && make scmconfig.h')
        # No -L %(system_root)s in `guile-config link'
        self.system ('cd %(builddir)s/libguile && make libpath.h')
        self.file_sub ([('''-L *%(system_root)s''', '-L')],
                       '%(builddir)s/libguile/libpath.h')
        targetpackage.TargetBuildSpec.compile (self)

    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        self.update_libtool ()

    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        majmin_version = '.'.join (self.expand ('%(version)s').split ('.')[0:2])
        
        self.dump ("prependdir GUILE_LOAD_PATH=$INSTALLER_PREFIX/share/guile/%(majmin_version)s\n",
                   '%(install_root)s/usr/etc/relocate/guile.reloc',
                   env=locals())
        
        ## can't assume that /usr/bin/guile is the right one.
        version = self.read_pipe ('''\
GUILE_LOAD_PATH=%(install_prefix)s/share/guile/* guile -e main -s  %(install_prefix)s/bin/guile-config --version 2>&1\
''').split ()[-1]
	#FIXME: c&p linux.py
        self.dump ('''\
#! /bin/sh
test "$1" = "--version" && echo "%(target_architecture)s-guile-config - Guile version %(version)s"
#test "$1" = "compile" && echo "-I $%(system_root)s/usr/include"
#test "$1" = "link" && echo "-L%(system_root)s/usr/lib -lguile -lgmp"
#prefix=$(dirname $(dirname $0))
prefix=%(system_root)s/usr
test "$1" = "compile" && echo "-I$prefix/include"
test "$1" = "link" && echo "-L$prefix/lib -lguile -lgmp"
exit 0
''',
             '%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config')
        os.chmod ('%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config' % self.get_substitution_dict (), 0755)


    
class Guile__mingw (Guile):
    def __init__ (self, settings):
        Guile.__init__ (self, settings)
        # Configure (compile) without -mwindows for console
        self.target_gcc_flags = '-mms-bitfields'


    def get_build_dependencies (self):
        return Guile.get_build_dependencies (self) +  ['regex-devel']
        
    def get_dependency_dict (self):
        d = Guile.get_dependency_dict (self)
        d['runtime'].append ('regex')
        return d

# FIXME: ugh, C&P to Guile__freebsd, put in cross-Guile?
    def configure_command (self):
        # watch out for whitespace
        builddir = self.builddir ()
        srcdir = self.srcdir ()


# don't set PATH_SEPARATOR; it will fuckup tool searching for the
# build platform.

        return (Guile.configure_command (self)
           + misc.join_lines ('''
LDFLAGS=-L%(system_root)s/usr/lib
CC_FOR_BUILD="
C_INCLUDE_PATH=
CPPFLAGS=
LIBRARY_PATH=
LDFLAGS=
cc
-I%(builddir)s
-I%(srcdir)s
-I%(builddir)s/libguile
-I.
-I%(srcdir)s/libguile"
'''))

    def config_cache_overrides (self, str):
        return str + '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_root)s/usr/lib"}
'''

    def configure (self):
        if 0: # using patch
            targetpackage.TargetBuildSpec.autoupdate (self)

        if 1:
            self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''',
                    '\\1')],
                   '%(srcdir)s/configure')

        Guile.configure (self)

        ## probably not necessary, but just be sure.
        for el in self.locate_files ('%(builddir)s', "Makefile"):
            self.file_sub ([('PATH_SEPARATOR = .', 'PATH_SEPARATOR = ;'),
                            ], el)
            
        self.file_sub ([
            #('^(allow_undefined_flag=.*)unsupported', '\\1'),
            ('-mwindows', ''),
            ],
               '%(builddir)s/libtool')
        self.file_sub ([
            #('^(allow_undefined_flag=.*)unsupported', '\\1'),
            ('-mwindows', ''),
            ],
               '%(builddir)s/guile-readline/libtool')

    def install (self):
        Guile.install (self)
        # dlopen-able .la files go in BIN dir, BIN OR LIB package
        self.system ('''mv %(install_root)s/usr/lib/lib*[0-9].la %(install_root)s/usr/bin''')

class Guile__linux (Guile):
    def compile_command (self):
        # FIXME: when not x-building, guile runs guile without
        # setting the proper LD_LIBRARY_PATH.
        return ('export LD_LIBRARY_PATH=%(builddir)s/libguile/.libs:$LD_LIBRARY_PATH;'
                + Guile.compile_command (self))

class Guile__linux__ppc (Guile__linux):
    def config_cache_overrides (self, str):
        return str + "\nguile_cv_have_libc_stack_end=no\n"

class Guile__freebsd (Guile):
    def config_cache_settings (self):
        return Guile.config_cache_settings (self) + '\nac_cv_type_socklen_t=yes'

    def set_mirror(self):
        self.with (version='1.8.0', mirror=download.gnu, format='gz')
        self.so_version = '17'

    def configure_command (self):
        # watch out for whitespace
        builddir = self.builddir ()
        srcdir = self.srcdir ()
        return (
            ''' guile_cv_use_csqrt="no" '''
           + Guile.configure_command (self)
           + misc.join_lines ('''\
CC_FOR_BUILD="
C_INCLUDE_PATH=
CPPFLAGS=
LIBRARY_PATH=
cc
-I%(builddir)s
-I%(srcdir)s
-I%(builddir)s/libguile
-I.
-I%(srcdir)s/libguile"
'''))

class Guile__darwin (Guile):
    def install (self):
        Guile.install (self)
        pat = self.expand ('%(install_root)s/usr/lib/libguile-srfi*.dylib')
        import glob
        for f in glob.glob (pat):
            directory = os.path.split (f)[0]
            src = os.path.basename (f)
            dst = os.path.splitext (os.path.basename (f))[0] + '.so'

            self.system ('cd %(directory)s && ln -s %(src)s %(dst)s', locals())
 
class Guile__darwin__x86 (Guile__darwin):
    def configure (self):
        Guile__darwin.configure (self)
        self.file_sub ([('guile-readline', '')],
                       '%(builddir)s/Makefile')
        
class Guile__cygwin (Guile):
    def __init__ (self, settings):
        Guile.__init__ (self, settings)
        self.with (version='1.8.1')

    # Using gub dependencies only would be nice, but
    # we need to a lot of gup.gub_to_distro_deps ().
    def GUB_get_dependency_dict (self):
        d = Guile.get_dependency_dict (self)
        d['runtime'].append ('cygwin')
        return d

    # Using gub dependencies only would be nice, but
    # we need to a lot of gup.gub_to_distro_deps ().
    def GUB_get_build_dependencies (self):
        return Guile.get_build_dependencies (self) + ['libiconv-devel']

    # FIXME: uses mixed gub/distro dependencies
    def get_dependency_dict (self):
        d = Guile.get_dependency_dict (self)
        d[''] += ['cygwin']
        d['devel'] += ['cygwin'] + ['bash']
        d['runtime'] += ['cygwin', 'crypt', 'libreadline6']
        return d
 
    # FIXME: uses mixed gub/distro dependencies
    def get_build_dependencies (self):
        return ['crypt', 'libgmp-devel', 'gettext-devel', 'libiconv', 'libtool', 'readline']

    def config_cache_overrides (self, str):
        return str + '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_root)s/usr/lib"}
'''
    def configure (self):
        if 1:
            self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''', '\\1')],
                           '%(srcdir)s/configure')
        Guile.configure (self)

        ## ugh code dup. 
        ## probably not necessary, but just be sure.
        for i in self.locate_files ('%(builddir)s', "Makefile"):
            self.file_sub ([
                ('PATH_SEPARATOR = .', 'PATH_SEPARATOR = ;'),
                ], i)

        self.file_sub ([
            ('^(allow_undefined_flag=.*)unsupported', '\\1'),
            ],
               '%(builddir)s/libtool')
        self.file_sub ([
            ('^(allow_undefined_flag=.*)unsupported', '\\1'),
            ],
               '%(builddir)s/guile-readline/libtool')

    def patch (self):
        pass

    # FIXME: we do most of this for all cygwin packages
    def category_dict (self):
        return {'': 'interpreters',
                'runtime': 'libs',
                'devel': 'devel libs',
                'doc': 'doc'}

    def description_dict (self):
        return {
            '': """The GNU extension language and Scheme interpreter - executables
Guile, the GNU Ubiquitous Intelligent Language for Extension, is a scheme
implementation designed for real world programming, supporting a
rich Unix interface, a module system, and undergoing rapid development.

`guile' is a scheme interpreter that can execute scheme scripts (with a
#! line at the top of the file), or run as an inferior scheme
process inside Emacs.
""",
            'runtime': '''The GNU extension language and Scheme interpreter - runtime
Guile shared object libraries and the ice-9 scheme module.  Guile is
the GNU Ubiquitous Intelligent Language for Extension.
''',
            'devel': """The GNU extension language and Scheme interpreter - development
`libguile.h' etc. C headers, aclocal macros, the `guile-snarf' and
`guile-config' utilities, and static `libguile.a' libraries for Guile,
the GNU Ubiquitous Intelligent Language for Extension.
""",
            'doc': """The GNU extension language and Scheme interpreter - documentation
This package contains the documentation for guile, including both
a reference manual (via `info guile'), and a tutorial (via `info
guile-tut').
""",
    }

class Guile__local (ToolBuildSpec, Guile):
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.set_mirror ()

    def configure_command (self):
        return (ToolBuildSpec.configure_command (self)
                + self.configure_flags ())

    def configure (self):
        ToolBuildSpec.configure (self)
        self.update_libtool ()

    def patch (self):
        self.autogen_sh()
        self.autoupdate ()

    def install (self):
        ToolBuildSpec.install (self)

        ## don't want local GUILE headers to interfere with compile.
        self.system ("rm -rf %(install_root)s/%(packaging_suffix_dir)s/usr/include/ %(install_root)s/%(packaging_suffix_dir)s/usr/bin/guile-config ")

    def get_build_dependencies (self):
        return ToolBuildSpec.get_build_dependencies (self) + Guile.get_build_dependencies (self)
