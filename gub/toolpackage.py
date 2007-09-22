from gub import misc
import os
import re

from gub import gubb

class ToolBuildSpec (gubb.BuildSpec):
    def configure_command (self):
        return (gubb.BuildSpec.configure_command (self)
            + misc.join_lines ('''
--prefix=%(local_prefix)s
'''))

    ## ugh: prefix= will trigger libtool relinks.
    def install_command (self):
        return '''make DESTDIR=%(install_root)s install'''

    def install (self):
        gubb.BuildSpec.install (self)
        self.wrap_executables ()
                
    def wrap_executables (self):
        def wrap (file):
            dir = os.path.dirname (file)
            base = os.path.basename (file)
            self.system ('mv %(file)s %(dir)s/.%(base)s', locals ())
            self.dump ('''#!/bin/sh
LD_LIBRARY_PATH=%(system_prefix)s/lib
%(system_prefix)s/bin/.%(file)s "$@"
''', file, env=locals ())
            os.chmod (file, 0755)
        self.map_locate (wrap, '%(install_prefix)s/bin', '*')
        self.map_locate (wrap, '%(install_root)s/%(local_prefix)s/bin', '*')

    def compile_command (self):
        return self.native_compile_command ()

    ## we need to tar up %(install_root)/%(prefix)
    def packaging_suffix_dir (self):
        return '%(system_root)s'

    def get_subpackage_names (self):
        return ['']

    def configure (self):
        gubb.BuildSpec.configure (self)
        self.update_libtool ()

    def get_substitution_dict (self, env={}):
        dict = {
            'C_INCLUDE_PATH': '%(local_prefix)s/include',
            'LIBRARY_PATH': '%(local_prefix)s/lib',
            'CPLUS_INCLUDE_PATH': '%(local_prefix)s/include',
            'LD_LIBRARY_PATH': '%(local_prefix)s/lib',
        }
        dict.update (env)
        d = gubb.BuildSpec.get_substitution_dict (self, dict).copy ()
        return d
