from gub import tools

class Fakechroot__tools (tools.AutoBuild):
    source = 'http://ftp.debian.nl/debian/pool/main/f/fakechroot/fakechroot_2.9.orig.tar.gz'
    def _get_build_dependencies (self):
        return [
            'libtool',
            'util-linux', # fakeroot script uses /usr/bin/getopt
            ]
    def libs (self):
        return '-ldl'
    def configure_variables (self):
        return (tools.AutoBuild.configure_variables (self)
                + ' CC=%(system_prefix)s/bin/%(toolchain_prefix)sgcc'
                + ' CCLD=%(system_prefix)s/bin/%(toolchain_prefix)sgcc'
                + ' CXX=%(system_prefix)s/bin/%(toolchain_prefix)sg++')
    def compile (self):
        tools.AutoBuild.compile (self)
        self.file_sub ([('BINDIR=.*', 'BINDIR=%(system_prefix)s/bin'),
                        ('PATHS=', 'PATHS=%(system_prefix)s/lib:'),],
                       '%(builddir)s/scripts/fakechroot')
