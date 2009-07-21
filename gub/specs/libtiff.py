from gub import target
from gub import tools

class Libtiff (target.AutoBuild):
    source = 'http://dl.maptools.org/dl/libtiff/tiff-3.8.2.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool', 'libjpeg-devel']

class Libtiff__tools (tools.AutoBuild, Libtiff):
    def _get_build_dependencies (self):
        return [
            'libtool',
            'libjpeg-devel',
#            'system::g++',
            ]
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ' --disable-cxx')
