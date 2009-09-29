from gub import target

class Fixesproto (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/fixesproto-4.0.tar.gz'
    dependencies = ['tools::libtool']
