from gub import repository
from gub import targetbuild

url='http://ftp.gnome.org/pub/GNOME/sources/libsigc++/2.0/libsigc++-2.0.17.tar.gz'

class Libsigxx (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
