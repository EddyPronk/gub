from gub import target

class Libxinerama (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/lib/libXinerama-1.0.3.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool', 'libx11-devel', 'xineramaproto-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
       return {'': [x.replace ('-devel', '')
                    for x in self._get_build_dependencies ()
                    if 'tools::' not in x and 'cross/' not in x]}
