from gub import target
from gub import tools

class Libtiff (target.AutoBuild):
    source = 'http://dl.maptools.org/dl/libtiff/tiff-3.8.2.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool', 'libjpeg-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
       return {'': [x.replace ('-devel', '')
                    for x in self._get_build_dependencies ()
                    if 'tools::' not in x and 'cross/' not in x]}

class Libtiff__tools (tools.AutoBuild):
    source = Libtiff.source
    def get_build_dependencies (self):
        return ['libtool', 'libjpeg-devel']
