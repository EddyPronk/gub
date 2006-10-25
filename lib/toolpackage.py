import download
import misc
import os
import re

import gub

class ToolBuildSpec (gub.BuildSpec):
    def configure_command (self):
        return (gub.BuildSpec.configure_command (self)
            + misc.join_lines ('''
--prefix=%(buildtools)s
'''))

    ## ugh: prefix= will trigger libtool relinks.
    def install_command (self):
        return '''make DESTDIR=%(install_root)s install'''

    def compile_command (self):
        return self.native_compile_command ()

    ## we need to tar up %(install_root)/%(prefix)
    def packaging_suffix_dir (self):
        return '%(system_root)s'

    def get_subpackage_names (self):
        return ['']

    def configure (self):
        gub.BuildSpec.configure (self)
        self.update_libtool ()

    def get_substitution_dict (self, env={}):
        dict = {
            'C_INCLUDE_PATH': '%(buildtools)s/include',
            'LIBRARY_PATH': '%(buildtools)s/lib',
            'CPLUS_INCLUDE_PATH': '%(buildtools)s/include',
        }
        dict.update (env)
        d = gub.BuildSpec.get_substitution_dict (self, dict).copy ()
        return d
