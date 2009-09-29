#
from gub import cygwin
from gub import gup
from gub.specs import libtool

class Libtool (libtool.Libtool):
    dependencies = gup.gub_to_distro_deps (libtool.Libtool.dependencies,
                                           cygwin.gub_to_distro_dict)
    def category_dict (self):
        return {'': 'Devel'}
    def install (self):
        libtool.Libtool.install (self)
        # configure nowadays (what m4?) has hardcoded /usr and /lib for Cygwin
        # instead of asking gcc
        self.file_sub ([('sys_lib_search_path_spec="/usr/lib /lib/w32api /lib /usr/local/lib"', 'sys_lib_search_path_spec="%(system_prefix)s/lib %(system_prefix)s/lib/w32api %(system_prefix)s/lib %(system_prefix)s/bin"')], '%(install_prefix)s/bin/libtool')
