from gub import target

class Libx11 (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/lib/libX11-1.1.5.tar.gz'
    def get_build_dependencies (self):
        return ['libtool', 'inputproto', 'kbproto', 'libxcb-devel', 'xextproto-devel', 'xproto-devel', 'xtrans-devel']
