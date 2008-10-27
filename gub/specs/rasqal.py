from gub import targetbuild

class Rasqal (targetbuild.AutoBuild):
    source = 'http://download.librdf.org/source/rasqal-0.9.16.tar.gz'
    def get_build_dependencies (self):
        return ['raptor-devel', 'libpcre-devel']

class Rasqal__mingw (Rasqal):
    patches = ['rasqal-0.9.16-mingw.patch']
