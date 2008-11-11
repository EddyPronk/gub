import os
#
from gub import build
from gub import context
from gub import misc
from gub import loggedos

def get_cross_build_dependencies (settings):
    return []

def change_target_package (bla):
    pass

class AutoBuild (build.AutoBuild):
    def configure_command (self):
        return (build.AutoBuild.configure_command (self)
                + self.configure_flags ()
                + self.configure_variables ())
    # FIXME: promoteme to build.py?  Most Fragile operation...
    def configure_flags (self):
        return misc.join_lines ('''
--prefix=%(system_prefix)s
--enable-shared
--enable-static
''')
    # FIXME: promoteme to build.py?  Most Fragile operation...
    def configure_variables (self):
        return misc.join_lines ('''
CFLAGS=-I%(system_prefix)s/include
LDFLAGS=-L%(system_prefix)s/lib
LD_LIBRARY_PATH=%(system_prefix)s/lib
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
            loggedos.chmod (logger, file, 0755)
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
        build.AutoBuild.configure (self)
        self.update_libtool ()

    def get_substitution_dict (self, env={}):
        dict = {
            'C_INCLUDE_PATH': '%(system_prefix)s/include'
            + misc.append_path (os.environ.get ('C_INCLUDE_PATH', '')),
            'LIBRARY_PATH': '%(system_prefix)s/lib'
            + misc.append_path (os.environ.get ('LIBRARY_PATH', '')),
            'CPLUS_INCLUDE_PATH': '%(system_prefix)s/include'
            + misc.append_path (os.environ.get ('CPLUS_INCLUDE_PATH', '')),
            'LD_LIBRARY_PATH': '%(system_prefix)s/lib'
            + misc.append_path (os.environ.get ('LD_LIBRARY_PATH', '')),
            'PATH': '%(system_prefix)s/bin:' + os.environ['PATH'],
        }
        dict.update (env)
        d = build.AutoBuild.get_substitution_dict (self, dict).copy ()
        return d

class MakeBuild (AutoBuild):
    def stages (self):
        return [s.replace ('configure', 'shadow') for s in AutoBuild.stages (self) if s not in ['autoupdate']]

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
