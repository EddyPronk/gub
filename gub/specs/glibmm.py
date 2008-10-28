from gub import targetbuild

class Glibmm (targetbuild.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.12/glibmm-2.12.10.tar.gz'
    def _get_build_dependencies (self):
        return ['glib', 'libsig++']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': self._get_build_dependencies ()}
