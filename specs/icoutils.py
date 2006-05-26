from toolpackage import ToolBuildSpecification

class Icoutils (ToolBuildSpecification):
    def __init__ (self, settings):
        ToolBuildSpecification.__init__ (self, settings)
        self.with (version='0.26.0',
                   mirror='http://savannah.nongnu.org/download/icoutils/icoutils-%(version)s.tar.gz',
                   ),
    def get_build_dependencies (self):
        return ['libpng-devel']
    def get_dependency_dict (self):
        return {'': ['libpng']}
