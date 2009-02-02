from gub import target

class Libpthread_stubs (target.AutoBuild):
    source = 'http://xcb.freedesktop.org/dist/libpthread-stubs-0.1.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool']
