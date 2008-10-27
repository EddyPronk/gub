from gub import targetbuild

class Rasqal (targetbuild.AutoBuild):
    source = 'http://download.librdf.org/source/rasqal-0.9.16.tar.gz'
    def get_build_dependencies (self):
        return ['raptor-devel', 'libpcre-devel']
    def config_script (self):
        return 'rasqal-config'

class Rasqal__mingw (Rasqal):
    patches = ['rasqal-0.9.16-mingw.patch']
