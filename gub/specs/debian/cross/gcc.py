from gub import cross
from gub import debian
from gub import mirrors

class Gcc (cross.Gcc):
    def __init__ (self, settings):
        cross.Gcc.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnu, version=debian.gcc_version,
                           format='bz2')

    def get_build_dependencies (self):
        return ['cross/binutils', 'libc6', 'libc6-dev', 'linux-kernel-headers']
    ## TODO: should detect whether libc supports TLS 
    def configure_command (self):
        return cross.Gcc.configure_command (self) + ' --disable-tls '
