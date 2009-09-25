from gub import tools

class Fakeroot_ng__tools (tools.AutoBuild):
    source = 'http://ftp.debian.nl/debian/pool/main/f/fakeroot-ng/fakeroot-ng_0.16.orig.tar.gz'
#    source = 'http://surfnet.dl.sourceforge.net/sourceforge/fakerootng/fakeroot-ng/0.17/fakeroot-ng-0.17.tar.gz'
    patches = [
        'fakeroot-ng-srcdir.patch',
        'fakeroot-ng-linux-2.4.patch'
        ]
    srcdir_build_broken = True
    def libs (self):
        return '-ldl'
    configure_variables = (tools.AutoBuild.configure_variables
                + ' CC=%(system_prefix)s/bin/%(toolchain_prefix)sgcc'
                + ' CCLD=%(system_prefix)s/bin/%(toolchain_prefix)sgcc'
                + ' CXX=%(system_prefix)s/bin/%(toolchain_prefix)sg++')
