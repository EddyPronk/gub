from gub import target

class Cairo (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/cairo-1.8.6.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool', 'fontconfig-devel', 'libpng-devel', 'libx11-devel', 'libxrender-devel', 'pixman-devel']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ''' LDFLAGS='%(rpath)s' ''')

class Cairo__mingw (Cairo):
    source = Cairo.source
    def get_build_dependencies (self):
        return [x for x in Cairo.get_build_dependencies (self)
                if 'libx' not in x]
