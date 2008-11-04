from gub.specs.cross import gcc

class Gcc__freebsd (gcc.Gcc):
    #source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.2/gcc-4.1.2.tar.bz2'
    #source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.1/gcc-4.1.1.tar.bz2'
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.3.2/gcc-4.3.2.tar.bz2'
    def get_build_dependencies (self):
        return gcc.Gcc.get_build_dependencies (self) + ['tools::mpfr']
