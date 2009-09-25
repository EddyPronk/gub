from gub.specs.cross import gcc
from gub import debian

class Gcc__debian (gcc.Gcc):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-' + debian.gcc_version + '/gcc-' + debian.gcc_version + '.tar.bz2'
    dependencies = ['cross/binutils', 'libc6', 'libc6-dev', 'linux-kernel-headers']
    ## TODO: should detect whether libc supports TLS 
    configure_flags = gcc.Gcc.configure_flags + ' --disable-tls '

class Gcc__debian__arm (Gcc__debian):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-3.4.6/gcc-3.4.6.tar.bz2'


