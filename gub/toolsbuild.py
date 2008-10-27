import os
import re
#
from gub import build
from gub import misc
from gub import loggedos

class ToolsBuild (build.UnixBuild):
    def configure_command (self):
        # FIXME: why is C_INCLUDE_PATH and LIBRARY_PATH from dict not
        # working, or not being picked-up by configure?
        return (build.UnixBuild.configure_command (self)
                + misc.join_lines ('''
--prefix=%(system_prefix)s
CFLAGS=-I%(system_prefix)s/include
LDFLAGS=-L%(system_prefix)s/lib
LD_LIBRARY_PATH=%(system_prefix)s/lib
'''))

    ## ugh: prefix= will trigger libtool relinks.
    def install_command (self):
        return '''make %(makeflags)s DESTDIR=%(install_root)s install'''

    def install (self):
        build.UnixBuild.install (self)
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
        build.UnixBuild.configure (self)
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
        d = build.UnixBuild.get_substitution_dict (self, dict).copy ()
        return d

class MakeBuild (ToolsBuild):
    def stages (self):
        return ['shadow' for s in [s for s in ToolsBuild.stages () if s not in ['autoupdate']]
                if s == 'configure']

class PythonBuild (ToolsBuild):
    def stages (self):
        return [s for s in TargetBuild.stages () if s not in ['autoupdate', 'configure']]
    def compile (self):
        self.system ('mkdir -p %(builddir)s')
    def install_command (self):
        return 'python %(srcdir)s/setup.py install --prefix=%(tools_prefix)s --root=%(install_root)s'

class SConsBuild (ToolsBuild):
    def stages (self):
        return [s for s in TargetBuild.stages () if s not in ['autoupdate', 'configure']]
    def compile_command (self):
        # SCons barfs on trailing / on directory names
        return ('scons PREFIX=%(system_prefix)s'
                ' PREFIX_DEST=%(install_root)s')
    def install_command (self):
        return self.compile_command () + ' install'
