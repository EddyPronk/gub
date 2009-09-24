from gub import target

class Libxau (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/libXau-1.0.4.tar.gz'
    dependencies = ['tools::libtool', 'xproto-devel']

class Libxau__freebsd (Libxau):
    dependencies = Libxau.dependencies + ['libiconv-devel']
