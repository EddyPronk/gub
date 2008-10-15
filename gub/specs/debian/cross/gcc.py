from gub.specs.cross import gcc
from gub import debian
from gub import mirrors

class Gcc (gcc.Gcc):
    def __init__ (self, settings, source):
        gcc.Gcc.__init__ (self, settings, source)
    source = mirrors.with_tarball (name='gcc', mirror=mirrors.gnu, version=debian.gcc_version,
                           format='bz2')
    def get_build_dependencies (self):
        return ['cross/binutils', 'libc6', 'libc6-dev', 'linux-kernel-headers']
    ## TODO: should detect whether libc supports TLS 
    def configure_command (self):
        return gcc.Gcc.configure_command (self) + ' --disable-tls '

class Gcc__debian__arm (Gcc):
    def __init__ (self, settings, source):
        gcc.Gcc.__init__ (self, settings, source)
    source = mirrors.with_tarball (name='gcc', mirror=mirrors.gnu, version='3.4.6', format='bz2')


