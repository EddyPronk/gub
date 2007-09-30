from gub import targetbuild
from gub import repository

url = 'http://ftp.isc.org/isc/dhcp/dhcp-3.0.6.tar.gz'

class Dhcp (targetbuild.TargetBuild):
    def __init__ (self, settings):
        targetbuild.TargetBuild.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url, strip_components=2))
    def get_subpackage_names (self):
        return ['']
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def configure_command (self):
        return '%(srcdir)s/configure linux-2.2'
    def makeflags (self):
        from gub import misc
        return misc.join_lines ('''
CC=%(toolchain_prefix)sgcc
AR=%(toolchain_prefix)sar
AS=%(toolchain_prefix)sas
LD=%(toolchain_prefix)sld
NM=%(toolchain_prefix)snm
RANLIB=%(toolchain_prefix)sranlib
STRIP=%(toolchain_prefix)sstrip
''')
    def license_file (self):
        return '%(srcdir)s/LICENSE'
