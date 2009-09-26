#
from gub import cygwin
from gub.specs import libtool

class Libtool (libtool.Libtool):
    def only_for_cygwin_untar (self):
        cygwin.untar_cygwin_src_package_variant2 (self, self.file_name ())
    # FIXME: we do most of this for all cygwin packages
    def get_dependency_dict (self): #cygwin
        d = libtool.Libtool.get_dependency_dict (self) # cygwin
        d[''].append ('cygwin')
        return d
    def category_dict (self):
        return {'': 'Devel'}
    def install (self):
        libtool.Libtool.install (self)
        # configure nowadays (what m4?) has hardcoded /usr and /lib for Cygwin
        # instead of asking gcc
        self.file_sub ([('sys_lib_search_path_spec="/usr/lib /lib/w32api /lib /usr/local/lib"', 'sys_lib_search_path_spec="%(system_prefix)s/lib %(system_prefix)s/lib/w32api %(system_prefix)s/lib %(system_prefix)s/bin"')], '%(install_prefix)s/bin/libtool')
