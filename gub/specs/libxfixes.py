from gub import target

class Libxfixes (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/libXfixes-4.0.3.tar.gz'
    dependencies = ['tools::libtool', 'fixesproto-devel', 'libx11-devel', 'libxau-devel', 'libxdmcp-devel']
