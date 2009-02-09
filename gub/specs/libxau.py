from gub import target

class Libxau (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/libXau-1.0.4.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool', 'xproto-devel']

class Libxau__freebsd (Libxau):
    def _get_build_dependencies (self):
        return Libxau._get_build_dependencies (self) + ['libiconv-devel']
