from gub import tools

class Fakechroot__tools (tools.AutoBuild):
    source = 'http://ftp.debian.nl/debian/pool/main/f/fakechroot/fakechroot_2.9.orig.tar.gz'
    def _get_build_dependencies (self):
        return ['libtool']
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ''' LDFLAGS='-L%(system_prefix)s/lib -ldl' '''
                + ' CC=%(system_prefix)s/bin/%(toolchain_prefix)sgcc'
                + ' CCLD=%(system_prefix)s/bin/%(toolchain_prefix)sgcc'
                + ' CXX=%(system_prefix)s/bin/%(toolchain_prefix)sg++'
                )
