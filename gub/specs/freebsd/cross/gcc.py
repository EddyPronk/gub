from gub.specs.cross import gcc as cross_gcc

class Gcc__freebsd (cross_gcc.Gcc):
    #source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.2/gcc-4.1.2.tar.bz2'
    #source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.1/gcc-4.1.1.tar.bz2'
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.3.2/gcc-4.3.2.tar.bz2'
    def _get_build_dependencies (self):
        return cross_gcc.Gcc._get_build_dependencies (self) + ['tools::mpfr']
