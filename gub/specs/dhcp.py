from gub import targetpackage
from gub import repository

url = 'http://ftp.isc.org/isc/dhcp/dhcp-3.0.5.tar.gz'

class Dhcp (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def configure_command (self):
        return '%(srcdir)s/configure linux-2.2'
    def makeflags (self):
        from gub import misc
        return misc.join_lines ('''
CC=%(tool_prefix)sgcc
AR=%(tool_prefix)sar
AS=%(tool_prefix)sas
LD=%(tool_prefix)sld
NM=%(tool_prefix)snm
RANLIB=%(tool_prefix)sranlib
STRIP=%(tool_prefix)sstrip
''')
    def license_file (self):
        return '%(srcdir)s/LICENSE'
