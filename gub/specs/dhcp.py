from gub import misc
from gub import target

class Dhcp (target.AutoBuild):
    #source = 'http://ftp.isc.org/isc/dhcp/dhcp-4.1.0a2.tar.gz'
    source = 'http://ftp.isc.org/isc/dhcp/dhcp-3.0.7.tar.gz&strip=2'
    srcdir_build_broken = True
    subpackage_names = ['']
    configure_command = '%(srcdir)s/configure linux-2.2'
    make_flags = misc.join_lines ('''
CC=%(toolchain_prefix)sgcc
AR=%(toolchain_prefix)sar
AS=%(toolchain_prefix)sas
LD=%(toolchain_prefix)sld
NM=%(toolchain_prefix)snm
RANLIB=%(toolchain_prefix)sranlib
STRIP=%(toolchain_prefix)sstrip
''')
