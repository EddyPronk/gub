from gub import tools

class Fakeroot_ng__tools (tools.AutoBuild):
    source = 'http://ftp.debian.nl/debian/pool/main/f/fakeroot-ng/fakeroot-ng_0.16.orig.tar.gz'
    patches = ['fakeroot-ng-srcdir.patch', 'fakeroot-ng-linux-2.4.patch']
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ' CFLAGS=-I%(builddir)s'
                + ' CC=%(system_prefix)s/bin/%(toolchain_prefix)sgcc'
                + ' CXX=%(system_prefix)s/bin/%(toolchain_prefix)sg++'
                )
    def configure (self):
        self.shadow ()
        tools.AutoBuild.configure (self)
