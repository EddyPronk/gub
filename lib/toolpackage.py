import misc
import os
import re

import gub

class ToolBuildSpec (gub.BuildSpec):
    def configure_command (self):
        return (gub.BuildSpec.configure_command (self)
            + misc.join_lines ('''
--prefix=%(local_prefix)s
'''))

    ## ugh: prefix= will trigger libtool relinks.
    def install_command (self):
        return '''make DESTDIR=%(install_root)s install'''

    def install (self):
        gub.BuildSpec.install (self)
        self.wrap_executables ()
                
    def wrap_executables (self):
        for e in (self.locate_files ('%(install_root)s/usr/bin', '*')
                  + self.locate_files ('%(install_root)s/%(local_prefix)s/bin',
                                       '*')):
            dir = os.path.dirname (e)
            file = os.path.basename (e)
            self.system ('mv %(e)s %(dir)s/.%(file)s', locals ())
            self.dump ('''#!/bin/sh
LD_LIBRARY_PATH=%(system_root)s/usr/lib
%(system_root)s/usr/bin/.%(file)s "$@"
''', e, env=locals ())
            os.chmod (e, 0755)

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
            'C_INCLUDE_PATH': '%(local_prefix)s/include',
            'LIBRARY_PATH': '%(local_prefix)s/lib',
            'CPLUS_INCLUDE_PATH': '%(local_prefix)s/include',
        }
        dict.update (env)
        d = gub.BuildSpec.get_substitution_dict (self, dict).copy ()
        return d
