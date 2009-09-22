from gub import target

class Cairomm (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/cairomm-1.8.0.tar.gz'
    def _get_build_dependencies (self):
        return ['cairo-devel', 'libsig++-devel']

class Cairomm__freebsd (Cairomm):
    def configure_variables (self):
        return (Cairomm.configure_command (self)
                + ' CFLAGS=-pthread CXXFLAGS=-pthread')
