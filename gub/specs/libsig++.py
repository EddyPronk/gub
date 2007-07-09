from gub import repository
from gub import targetpackage

url='http://ftp.gnome.org/pub/GNOME/sources/libsigc++/2.0/libsigc++-2.0.17.tar.gz'

class Libsigxx (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
