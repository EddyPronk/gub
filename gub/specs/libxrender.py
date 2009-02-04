from gub import target

class Libxrender (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/libXrender-0.9.4.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool', 'libx11-devel', 'libxdmcp-devel', 'renderproto-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
       return {'': [x.replace ('-devel', '')
                    for x in self._get_build_dependencies ()
                    if 'tools::' not in x and 'cross/' not in x]}
