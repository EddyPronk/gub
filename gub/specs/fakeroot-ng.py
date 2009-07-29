from gub import tools

class Fakeroot_ng__tools (tools.AutoBuild):
    source = 'http://ftp.debian.nl/debian/pool/main/f/fakeroot-ng/fakeroot-ng_0.16.orig.tar.gz'
#    source = 'http://surfnet.dl.sourceforge.net/sourceforge/fakerootng/fakeroot-ng/0.17/fakeroot-ng-0.17.tar.gz'
    patches = [
        'fakeroot-ng-srcdir.patch',
        'fakeroot-ng-linux-2.4.patch'
        ]
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ''' LDFLAGS='-L%(system_prefix)s/lib64 -L%(system_prefix)s/lib %(rpath)s %(rpath)s64 -ldl' '''
                + ' CFLAGS=-I%(builddir)s'
                + ' CC=%(system_prefix)s/bin/%(toolchain_prefix)sgcc'
                + ' CXX=%(system_prefix)s/bin/%(toolchain_prefix)sg++'
                )
    def configure (self):
        self.shadow ()
        tools.AutoBuild.configure (self)
