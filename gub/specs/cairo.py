from gub import target

class Cairo (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/cairo-1.8.6.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool', 'fontconfig-devel', 'libpng-devel', 'libx11-devel', 'libxrender-devel', 'pixman-devel']
