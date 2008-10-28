from gub import build
from gub import debian

class Libc6_dev (build.BinaryBuild, build.SdkBuild):
    source = 'http://ftp.debian.org/debian/pool/main/g/glibc/libc6-dev_' + debian.get_packages ()['libc6-dev'].version () + '_%%(package_arch)s.deb&strip=0'
    def untar (self):
        build.BinaryBuild.untar (self)
        # FIXME: this rewiring breaks ld badly, it says
        #     i686-linux-ld: cannot find /home/janneke/bzr/gub/target/i686-linux/system/lib/libc.so.6 inside /home/janneke/bzr/gub/target/i686-linux/system/
        # although that file exists.  Possibly rewiring is not necessary,
        # but we can only check on non-linux platform.
        # self.file_sub ([(' /', ' %(system_root)s/')],
        #               '%(srcdir)s/root/usr/lib/libc.so')

        for i in ('pthread.h', 'bits/sigthread.h'):
            self.file_sub ([('__thread', '___thread')],
                           '%(srcdir)s/usr/include/%(i)s',
                           env=locals ())
            
        self.system ('rm -rf  %(srcdir)s/usr/include/asm/  %(srcdir)s/usr/include/linux ')
