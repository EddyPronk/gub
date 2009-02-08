from gub import target

class Inputproto (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/inputproto-1.4.4.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool']
