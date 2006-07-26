import os
import re

import cross
import download
import gub
import gup
import linux
import misc
import targetpackage

import debian_unstable

class Mipsel_runtime (gub.BinarySpec, gub.SdkBuildSpec):
    pass

#http://ftp.debian.org/debian/pool/main/g/glibc/libc6_2.3.2.ds1-22sarge3_mipsel.deb
#http://ftp.debian.org/debian/pool/main/g/glibc/libc6-dev_2.3.2.ds1-22sarge3_mipsel.deb
#http://ftp.debian.org/debian/pool/main/l/linux-kernel-headers/linux-kernel-headers_2.5.999-test7-bk-17_mipsel.deb

class Gcc_34 (cross.Gcc):
    def __init__ (self, settings):
        cross.Gcc.__init__ (self, settings)
        # FIXME: this overwrites cross.Gcc's dict, so that
        # the default gcc's c++ is also not built?
        #self.settings.__dict__['no-c++'] = True

    def configure_command (self):
        return misc.join_lines (cross.Gcc.configure_command (self)
                               + '''
--program-suffix=-3.4
--with-ar=%(crossprefix)s/bin/%(target_architecture)s-ar
--with-nm=%(crossprefix)s/bin/%(target_architecture)s-nm
''')

    def configure (self):
        cross.Gcc.configure (self)
        #FIXME: --with-ar, --with-nm does not work?
        for i in ('ar', 'nm', 'ranlib'):
            self.system ('cd %(crossprefix)s/bin && ln -sf %(target_architecture)s-%(i)s %(target_architecture)s-%(i)s-3.4', env=locals ())
                
    def install (self):
        cross.Gcc.install (self)
        # get rid of duplicates
        self.system ('''
rm -f %(install_root)s/usr/lib/libgcc_s.so
rm -f %(install_root)s/usr/lib/libgcc_s.so.1
rm -f %(install_root)s/usr/cross/lib/libiberty.a
rm -rf %(install_root)s/usr/cross/info
rm -rf %(install_root)s/usr/cross/man
rm -rf %(install_root)s/usr/cross/share/locale
''')

def get_cross_packages (settings):
    lst = [
        #linux.Libc6 (settings).with (version='2.2.5-11.8',
        linux.Libc6 (settings).with (version='2.3.2.ds1-22sarge3',
                                     mirror=download.glibc_deb,
                                     format='deb'),
        #linux.Libc6_dev (settings).with (version='2.2.5-11.8',
        linux.Libc6_dev (settings).with (version='2.3.2.ds1-22sarge3',
                                         mirror=download.glibc_deb,
                                         format='deb'),
        #linux.Linux_kernel_headers (settings).with (version='2.6.13+0rc3-2',
        linux.Linux_kernel_headers (settings).with (version='2.5.999-test7-bk-17',
                                                    mirror=download.lkh_deb,
                                                    format='deb'),
        cross.Binutils (settings).with (version='2.16.1', format='bz2'),
        cross.Gcc (settings).with (version='4.1.1',
                                   mirror=download.gcc_41,
                                   format='bz2'),
        Gcc_34 (settings).with (version='3.4.6',
                             mirror=(download.gnubase
                                     + '/gcc/gcc-3.4.6/gcc-3.4.6.tar.bz2'),
                             format='bz2'),
        ]
    return lst

# unstable
def get_unstable_cross_packages (settings):
    lst = [
        linux.Libc6 (settings).with (version='2.3.2.ds1-22sarge3',
                                     mirror=download.glibc_deb,
                                     format='deb'),
        #linux.Libc6_dev (settings).with (version='2.2.5-11.8',
        linux.Libc6_dev (settings).with (version='2.3.2.ds1-22sarge3',
                                         mirror=download.glibc_deb,
                                         format='deb'),
        #linux.Linux_kernel_headers (settings).with (version='2.6.13+0rc3-2',
        linux.Linux_kernel_headers (settings).with (version='2.5.999-test7-bk-17',
                                                    mirror=download.lkh_deb,
                                                    format='deb'),
        cross.Binutils (settings).with (version='2.16.1', format='bz2'),
        cross.Gcc (settings).with (version='4.1.1',
                                   mirror=download.gcc_41,
                                   format='bz2'),
        Gcc_34 (settings).with (version='3.4.6',
                             mirror=(download.gnubase
                                     + '/gcc/gcc-3.4.6/gcc-3.4.6.tar.bz2'),
                             format='bz2'),
        ]
    return lst



def change_target_packages (packages):
    cross.change_target_packages (packages)
    cross.set_framework_ldpath ([p for p in packages.values ()
                                 if isinstance (p,
                                                targetpackage.TargetBuildSpec)])
    return packages
