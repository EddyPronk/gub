from gub import target

class Xineramaproto (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/proto/xineramaproto-1.1.2.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool']
