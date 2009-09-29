from gub import target

class Libxrender (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/libXrender-0.9.4.tar.gz'
    dependencies = ['tools::libtool', 'libx11-devel', 'libxdmcp-devel', 'renderproto-devel']
    configure_flags = (target.AutoBuild.configure_flags
                       + ' --disable-malloc0returnsnull')
