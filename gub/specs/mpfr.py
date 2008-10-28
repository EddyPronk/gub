from gub import toolsbuild

class Mpfr__tools (toolsbuild.AutoBuild):
    source = 'http://www.mpfr.org/mpfr-2.3.2/mpfr-2.3.2.tar.gz'
    def get_build_dependencies (self):
        return ['libtool', 'gmp']
