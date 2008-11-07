from gub import tools

class Libtiff__tools (tools.AutoBuild):
    source = 'http://dl.maptools.org/dl/libtiff/tiff-3.8.2.tar.gz'
    def get_build_dependencies (self):
        return ['libtool']
