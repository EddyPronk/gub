from gub import targetbuild

class Libxml_xx_ (targetbuild.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/libxml++/2.18/libxml++-2.18.1.tar.gz'
    def _get_build_dependencies (self):
        return ['glibmm']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': self._get_build_dependencies ()}
