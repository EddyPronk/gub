from gub import repository
from gub import targetpackage

url='http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.12/glibmm-2.12.10.tar.gz'

class Glibmm (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
    def get_build_dependencies (self):
        return ['glib', 'libsig++']
    def get_dependency_dict (self):
        return {'': self.get_build_dependencies ()}
