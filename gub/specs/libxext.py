from gub import target

class Libxext (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/lib/libXext-1.0.4.tar.gz'
    def _get_build_dependencies (self):
        return ['libtool', 'libx11-devel']
