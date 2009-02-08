from gub import target

class Xcb_proto (target.AutoBuild):
    source = 'http://xcb.freedesktop.org/dist/xcb-proto-1.3.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool']
