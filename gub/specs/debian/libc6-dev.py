from gub import gubb
from gub import debian
from gub import mirrors

class Libc6_dev (gubb.BinarySpec, gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.BinarySpec.__init__ (self, settings)
        self.with_template  (version=debian.get_packages ()['libc6-dev'].version (),
                   strip_components=0,
                   mirror=mirrors.glibc_deb,
# FIXME: we do not mirror all 12 debian arch's,
#                   mirror=mirrors.lilypondorg_deb,
                   format='deb')
    def untar (self):
        gubb.BinarySpec.untar (self)
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
