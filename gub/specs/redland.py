from gub import targetbuild

class Redland (targetbuild.AutoBuild):
    source = 'http://download.librdf.org/source/rasqal-0.9.16.tar.gz'
    def get_build_dependencies (self):
        return ['rasqal-devel']
