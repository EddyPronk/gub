from gub import targetpackage

class Bash (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='3.2',
                   mirror='ftp://ftp.cwru.edu/pub/bash/bash-3.2.tar.gz',
                   format='bz2')

    def get_build_dependencies (self):
        return ['libtool', 'gettext-devel']
