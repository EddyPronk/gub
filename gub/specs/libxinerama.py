from gub import target

class Libxinerama (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/lib/libXinerama-1.0.3.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool', 'libx11-devel', 'xineramaproto-devel']
