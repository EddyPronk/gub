from gub import misc
import os
import re

from gub import build
from gub import loggedos

class ToolsBuild (build.UnixBuild):
    def configure_command (self):
        return (build.UnixBuild.configure_command (self)
            + misc.join_lines ('''
--prefix=%(tools_prefix)s
'''))

    ## ugh: prefix= will trigger libtool relinks.
    def install_command (self):
        return '''make DESTDIR=%(install_root)s install'''

    def install (self):
        build.UnixBuild.install (self)
        self.wrap_executables ()

    def wrap_executables (self):
        def wrap (logger, file):
            dir = os.path.dirname (file)
            base = os.path.basename (file)
            cmd = self.expand ('mv %(file)s %(dir)s/.%(base)s', locals ())
            loggedos.system (logger, cmd)
            loggedos.dump_file (logger, self.expand('''#!/bin/sh
LD_LIBRARY_PATH=%(system_prefix)s/lib
%(system_prefix)s/bin/.%(base)s "$@"
''', locals()), file)
            loggedos.chmod (logger, file, 0755)
        self.map_locate (wrap, '%(install_prefix)s/bin', '*')
        self.map_locate (wrap, '%(install_root)s/%(tools_prefix)s/bin', '*')

    def compile_command (self):
        return self.native_compile_command ()

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
            'C_INCLUDE_PATH': '%(toolchain_prefix)s/include',
            'LIBRARY_PATH': '%(toolchain_prefix)s/lib',
            'CPLUS_INCLUDE_PATH': '%(toolchain_prefix)s/include',
            'LD_LIBRARY_PATH': '%(toolchain_prefix)s/lib',
        }
        dict.update (env)
        d = build.UnixBuild.get_substitution_dict (self, dict).copy ()
        return d
