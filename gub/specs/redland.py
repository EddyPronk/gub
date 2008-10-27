from gub import targetbuild

class Redland (targetbuild.AutoBuild):
    source = 'http://download.librdf.org/source/redland-1.0.8.tar.gz'
    def get_build_dependencies (self):
        return ['rasqal-devel']
    def config_script (self):
        return 'redland-config'
