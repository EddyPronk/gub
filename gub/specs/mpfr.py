from gub import tools

class Mpfr__tools (tools.AutoBuild):
    source = 'http://www.mpfr.org/mpfr-2.3.2/mpfr-2.3.2.tar.gz'
    def get_build_dependencies (self):
        return ['libtool', 'gmp']
