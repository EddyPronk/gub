from gub import repository
from gub import targetbuild

url='http://ftp.gnome.org/pub/GNOME/sources/libsigc++/2.0/libsigc++-2.0.17.tar.gz'

class Libsig_xx_ (targetbuild.TargetBuild):
    source = mirrors.with_vc (repository.TarBall (self.settings.downloads, url))
