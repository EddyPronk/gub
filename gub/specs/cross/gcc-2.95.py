from gub.specs.cross import gcc as cross_gcc

class Gcc_2_95 (cross_gcc.Gcc):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-2.95.3/gcc-everything-2.95.3.tar.gz'
    configure_flags = (cross_gcc.Gcc.configure_flags
                       + ' --program-suffix=-2.95')
