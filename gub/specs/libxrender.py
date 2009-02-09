from gub import target

class Libxrender (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/libXrender-0.9.4.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool', 'libx11-devel', 'libxdmcp-devel', 'renderproto-devel']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' --disable-malloc0returnsnull')
