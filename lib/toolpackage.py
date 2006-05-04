import re
import gub
import download
import misc
import os

class Tool_package (gub.Package):
    def configure_command (self):
        return (gub.Package.configure_command (self)
            + misc.join_lines ('''
--prefix=%(buildtools)s/
'''))

    ## ugh: this will trigger libtool relinks. 
    def install_command (self):
        return '''make DESTDIR=%(install_root)s prefix=/usr install'''

    def compile_command (self):
        return self.native_compile_command ()

    def package (self):
        self.system ('''
tar -C %(install_root)s/ -zcf %(gub_uploads)s/%(gub_name)s .
''')

    def get_substitution_dict (self, env={}):
        dict = {
            'C_INCLUDE_PATH': '%(buildtools)s/include',
            'LIBRARY_PATH': '%(buildtools)s/lib',
            'CPLUS_INCLUDE_PATH': '%(buildtools)s/include',
        }
        dict.update (env)
        d =  gub.Package.get_substitution_dict (self, dict).copy()
        return d
