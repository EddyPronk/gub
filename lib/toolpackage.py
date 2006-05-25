import re
import gub
import download
import misc
import os

class Tool_package (gub.BuildSpecification):
    def configure_command (self):
        return (gub.BuildSpecification.configure_command (self)
            + misc.join_lines ('''
--prefix=%(buildtools)s/
'''))

    ## ugh: this will trigger libtool relinks. 
    def install_command (self):
        return '''make DESTDIR=%(install_root)s prefix=/usr install'''

    def compile_command (self):
        return self.native_compile_command ()

    def get_packages (self):
        return [self.get_tool_package()]
    def get_tool_package (self):
        p = gub.PackageSpecification (self.os_interface)
        p.set_dict (self.get_substitution_dict(), '')
        p._file_specs = ['/']
        return p
    
    def get_substitution_dict (self, env={}):
        dict = {
            'C_INCLUDE_PATH': '%(buildtools)s/include',
            'LIBRARY_PATH': '%(buildtools)s/lib',
            'CPLUS_INCLUDE_PATH': '%(buildtools)s/include',
        }
        dict.update (env)
        d =  gub.BuildSpecification.get_substitution_dict (self, dict).copy()
        return d
