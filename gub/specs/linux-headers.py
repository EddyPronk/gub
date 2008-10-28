from gub import build

class Linux_headers (build.BinaryBuild, build.SdkBuild):
    source = 'http://www.nl.kernel.org/pub/linux/kernel/v2.4/linux-2.4.34.tar.bz2&name=linux-headers'
    # HMm, is this more handy than patch ():pass in BinaryBuild?
    # possibly we should simply override install (), but that is
    # always a problem because install ()
    def stages (self):
        return misc.list_insert_before (build.BinaryBuild.stages (self),
                                        'install', 'patch')
    def get_subpackage_names (self):
        return ['']
    def patch (self):
        self.system ('''
cd %(srcdir)s && yes yes | make ARCH=%(package_arch)s oldconfig symlinks include/linux/version.h
#cd %(srcdir)s && yes yes | make ARCH=i386 oldconfig
#cd %(srcdir)s && make ARCH=%(package_arch)s symlinks include/linux/version.h
cd %(srcdir)s && mv include .include
cd %(srcdir)s && rm -rf *
cd %(srcdir)s && mkdir usr
cd %(srcdir)s && mv .include usr/include
cd %(srcdir)s && rm -f\
 usr/include/scsi/sg.h\
 usr/include/scsi/scsi.h\
 usr/include/scsi/scsi_ioctl.h\
 usr/include/net/route.h
''')

from gub import misc
linux_kernel_headers = misc.load_spec ('debian/linux-kernel-headers')

class Linux_headers__debian (linux_kernel_headers.Linux_kernel_headers):
#        debian.init_dependency_resolver (settings)
# FIXME: we do not mirror all 12 debian arch's,
    source = 'http://ftp.debian.org/debian/pool/main/l/linux-kernel-headers/linux-kernel-headers_2.5.999-test7-bk-17_%%(package_arch)s.deb&strip=0' 

Linux_headers__linux__ppc = Linux_headers__debian
#Linux_headers__linux__64 = Linux_headers__debian
Linux_headers__linux__arm = Linux_headers__debian
Linux_headers__linux__arm__softfloat = Linux_headers__debian
Linux_headers__linux__arm__vfp = Linux_headers__debian
Linux_headers__linux__mipsel = Linux_headers__debian

class Linux_headers__linux__64 (Linux_headers__debian):
# FIXME: we do not mirror all 12 debian arch's,
    source = 'http://ftp.debian.org/debian/pool/main/l/linux-kernel-headers/linux-kernel-headers_2.6.18-7_%%(package_arch)s.deb&strip=0' 
