from gub import targetbuild

class Dhcp (targetbuild.AutoBuild):
    #source = 'http://ftp.isc.org/isc/dhcp/dhcp-4.1.0a2.tar.gz'
    source = 'http://ftp.isc.org/isc/dhcp/dhcp-3.0.7.tar.gz&strip=2'
    def get_subpackage_names (self):
        return ['']
    def configure_command (self):
        return '%(srcdir)s/configure linux-2.2'
    def configure (self):
        self.shadow ()
        targetbuild.AutoBuild.configure (self)
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
