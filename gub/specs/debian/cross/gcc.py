from gub.specs.cross import gcc
from gub import debian

class Gcc__debian (gcc.Gcc):
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-' + debian.gcc_version + '/gcc-' + debian.gcc_version + '.tar.bz2'
    def get_build_dependencies (self):
        return ['cross/binutils', 'libc6', 'libc6-dev', 'linux-kernel-headers']
    ## TODO: should detect whether libc supports TLS 
    def configure_command (self):
        return gcc.Gcc.configure_command (self) + ' --disable-tls '

class Gcc__debian__arm (Gcc__debian):
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-3.4.6/gcc-3.4.6.tar.bz2'


