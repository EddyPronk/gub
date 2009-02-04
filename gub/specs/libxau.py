from gub import target

class Libxau (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/libXau-1.0.4.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool', 'xproto-devel']
