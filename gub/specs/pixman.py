from gub import target

class Pixman (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/pixman-0.13.2.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool']
