import os
#
from gub import build
from gub import context
from gub import loggedos
from gub import misc
from gub import octal

def get_cross_build_dependencies (settings):
    return []

def change_target_package (package):
    package_auto_dependency_dict (package)

def package_auto_dependency_dict (package):
    '''Generate get_build_dependencies () and get_dependency_dict ({'':})
    from _get_build_dependencies ().
    
    For most packages, this either removes the need of having both,
    or adds the dict where it was missing.
    '''
    if (not package.get_build_dependencies ()
        and not package.get_dependency_dict ().get ('', None)
        and not package.get_dependency_dict ().get ('devel', None)
        and ('_get_build_dependencies' in
             dict (context.object_get_methods (package)).keys ())):
        def get_build_dependencies (foo):
            # If a package depends on tools::libtool, ie not on
            # libltdl, we still also need <target-arch>::libtool,
            # because of our update_libtool ().  We fix this here,
            # because it's not a package's real dependency but rather
            # a detail of our libtool breakage fixup.
            if not 'cross' in package.name ():
                return [name.replace ('tools::libtool', 'libtool')
                        for name in package._get_build_dependencies ()]
            return package._get_build_dependencies ()
        package.get_build_dependencies \
                = misc.MethodOverrider (package.nop, get_build_dependencies)
        def get_dependency_dict (foo):
            d = {'': [x.replace ('-devel', '')
                         for x in package._get_build_dependencies ()
                         if 'tools::' not in x and 'cross/' not in x]}
            if 'runtime' in package.get_subpackage_names ():
                d[''] += [package.name () + '-runtime']
            if package.platform_name () != 'tools':
                d['devel'] = ([x for x in package._get_build_dependencies ()
                               if 'tools::' not in x and 'cross/' not in x]
                              + [package.name ()])
            return d
        package.get_dependency_dict \
                = misc.MethodOverrider (package.nop, get_dependency_dict)

class AutoBuild (build.AutoBuild):
    def configure_command (self):
        return (build.AutoBuild.configure_command (self)
                + self.configure_flags ()
                + self.configure_variables ())
    # FIXME: promoteme to build.py?  Most Fragile operation...
    def configure_flags (self):
        config_cache = ''
        if self.config_cache_settings ():
            config_cache = '\n--config-cache'
        return misc.join_lines ('''
--prefix=%(system_prefix)s
--enable-shared
--enable-static
''' + config_cache)
    # FIXME: promoteme to build.py?  Most Fragile operation...
    def configure_variables (self):
        return misc.join_lines ('''
CFLAGS=-I%(system_prefix)s/include
LDFLAGS=-L%(system_prefix)s/lib
''')

    ## ugh: prefix= will trigger libtool relinks.
    def install_command (self):
        return '''make %(makeflags)s DESTDIR=%(install_root)s install'''

    def broken_install_command (self):
        # FIXME: use sysconfdir=%(install_PREFIX)s/etc?  If
        # so, must also ./configure that way
        return misc.join_lines ('''make %(makeflags)s install
bindir=%(install_root)s/%(system_prefix)s/bin
aclocaldir=%(install_root)s/%(system_prefix)s/share/aclocal
datadir=%(install_root)s/%(system_prefix)s/share
exec_prefix=%(install_root)s/%(system_prefix)s
gcc_tooldir=%(install_root)s/%(system_prefix)s
includedir=%(install_root)s/%(system_prefix)s/include
infodir=%(install_root)s/%(system_prefix)s/share/info
libdir=%(install_root)s/%(system_prefix)s/lib
libexecdir=%(install_root)s/%(system_prefix)s/lib
mandir=%(install_root)s/%(system_prefix)s/share/man
prefix=%(install_root)s/%(system_prefix)s
sysconfdir=%(install_root)s/%(system_prefix)s/etc
tooldir=%(install_root)s/%(system_prefix)s
''')

    def install (self):
        build.AutoBuild.install (self)
        # conditional on use of rpath, depending on shared libs?
        self.wrap_executables ()

    def wrap_executables (self):
        def wrap (logger, file):
            dir = os.path.dirname (file)
            base = os.path.basename (file)
            cmd = self.expand ('mv %(file)s %(dir)s/.%(base)s', locals ())
            loggedos.system (logger, cmd)
            loggedos.dump_file (logger, self.expand ('''#!/bin/sh
LD_LIBRARY_PATH=%(system_prefix)s/lib
%(system_prefix)s/bin/.%(base)s "$@"
''', locals ()), file)
            loggedos.chmod (logger, file, octal.o755)
        self.map_locate (wrap, '%(install_prefix)s/bin', '*')
        self.map_locate (wrap, '%(install_root)s/%(tools_prefix)s/bin', '*')

    def compile_command (self):
        return self.native_compile_command () + ' %(makeflags)s'

    ## we need to tar up %(install_root)/%(prefix)
    def packaging_suffix_dir (self):
        return '%(system_root)s'

    def get_subpackage_names (self):
        return ['']

    def configure (self):
        self.config_cache ()
        build.AutoBuild.configure (self)
        self.update_libtool ()

    # FIXME: make Multiple-Inheritance-safe, ie
    #    class Foo__tools (tools.AutoBuild, Foo)
    # must not set a config cache or target's rpath updating libtool
    # Hmm.
    def config_cache_settings (self):
        return ''
    def update_libtool (self):
        build.AutoBuild.update_libtool (self)

    def get_substitution_dict (self, env={}):
        dict = {
            'C_INCLUDE_PATH': '%(system_prefix)s/include'
            + misc.append_path (os.environ.get ('C_INCLUDE_PATH', '')),
            'CPLUS_INCLUDE_PATH': '%(system_prefix)s/include'
            + misc.append_path (os.environ.get ('CPLUS_INCLUDE_PATH', '')),
            'LIBRARY_PATH': '%(system_prefix)s/lib'
            + misc.append_path (os.environ.get ('LIBRARY_PATH', '')),
            'LIBRESTRICT_IGNORE': '%(system_prefix)s/bin/make',
            'PATH': '%(system_prefix)s/bin:' + os.environ['PATH'],
        }
        dict.update (env)
        d = build.AutoBuild.get_substitution_dict (self, dict).copy ()
        return d

class MakeBuild (AutoBuild):
    def stages (self):
        return [s.replace ('configure', 'shadow') for s in AutoBuild.stages (self) if s not in ['autoupdate']]

class ShBuild (AutoBuild):
    def stages (self):
        return [s.replace ('configure', 'shadow') for s in AutoBuild.stages (self) if s not in ['autoupdate']]
    def compile_command (self):
        return 'bash build.sh'
    def install_command (self):
        print ('Override me.')
        assert False

class PythonBuild (AutoBuild):
    def stages (self):
        return [s for s in AutoBuild.stages (self) if s not in ['autoupdate', 'configure']]
    def compile (self):
        self.system ('mkdir -p %(builddir)s')
    def install_command (self):
        return 'python %(srcdir)s/setup.py install --prefix=%(tools_prefix)s --root=%(install_root)s'

class SConsBuild (AutoBuild):
    def stages (self):
        return [s for s in AutoBuild.stages (self) if s not in ['autoupdate', 'configure']]
    def compile_command (self):
        # SCons barfs on trailing / on directory names
        return ('scons PREFIX=%(system_prefix)s'
                ' PREFIX_DEST=%(install_root)s')
    def install_command (self):
        return self.compile_command () + ' install'

class BjamBuild_v2 (MakeBuild):
    def _get_build_dependencies (self):
        return ['boost-jam']
    def patch (self):
        MakeBuild.patch (self)
    def compile_command (self):
        return misc.join_lines ('''
bjam
-q
--layout=system
--builddir=%(builddir)s
--prefix=%(system_prefix)s
--exec-prefix=%(system_prefix)s
--libdir=%(system_prefix)s/lib
--includedir=%(system_prefix)s/include
--verbose
cxxflags=-fPIC
toolset=gcc
debug-symbols=off
link=shared
runtime-link=shared
threading=multi
release
''')
    def install_command (self):
        return (self.compile_command ()
                + ' install').replace ('=%(system_prefix)s', '=%(install_root)s%(system_prefix)s')

class NullBuild (AutoBuild):
    def stages (self):
        return ['patch', 'install', 'package', 'clean']
    def get_subpackage_names (self):
        return ['']
    def install (self):
        self.system ('mkdir -p %(install_root)s%(system_prefix)s')
