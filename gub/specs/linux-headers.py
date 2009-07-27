from gub import build
from gub import context

class Linux_headers (build.BinaryBuild, build.SdkBuild):
    source = 'http://www.nl.kernel.org/pub/linux/kernel/v2.4/linux-2.4.34.tar.bz2&name=linux-headers'
    # HMm, is this more handy than patch ():pass in BinaryBuild?
    # possibly we should simply override install (), but that is
    # always a problem because install ()
    def stages (self):
        return misc.list_insert_before (build.BinaryBuild.stages (self),
                                        'install', 'patch')
    @context.subst_method
    def linux_arch (self):
        return '%(package_arch)s'
    def get_subpackage_names (self):
        return ['']
    def patch (self):
        self.file_sub ([('[.] [.]config-is-not', '. ./.config-is-not'),],
                       '%(srcdir)s/scripts/Configure')
        self.system ('''
#let's not use patch, and certainly not circumventing patch mechanism
#cd %(srcdir)s && patch -p1 < %(patchdir)s/linux-headers-2.4.34-posix-fix.patch
cd %(srcdir)s && yes yes | make ARCH=%(linux_arch)s oldconfig symlinks include/linux/version.h
cd %(srcdir)s && rm -f include/asm
cd %(srcdir)s && mv include/asm-%(linux_arch)s include/asm
cd %(srcdir)s && rm -rfv include/asm-*
cd %(srcdir)s && mv include .include
cd %(srcdir)s && rm -rf *
cd %(srcdir)s && mkdir -p ./%(prefix_dir)s
cd %(srcdir)s && mv .include ./%(prefix_dir)s/include
''')
        # Duplicated in libc, remove here.
        self.system ('''
cd %(srcdir)s && rm -f\
 ./%(prefix_dir)s/include/scsi/sg.h\
 ./%(prefix_dir)s/include/scsi/scsi.h\
 ./%(prefix_dir)s/include/scsi/scsi_ioctl.h\
 ./%(prefix_dir)s/include/net/route.h
''')

from gub import misc
linux_kernel_headers = misc.load_spec ('debian/linux-kernel-headers')

class Linux_headers__debian (linux_kernel_headers.Linux_kernel_headers):
#        debian.init_dependency_resolver (settings)
# FIXME: we do not mirror all 12 debian arch's,
    source = 'http://ftp.debian.org/debian/pool/main/l/linux-kernel-headers/linux-kernel-headers_2.5.999-test7-bk-17_%(package_arch)s.deb&strip=0' 

Linux_headers__linux__ppc = Linux_headers__debian
#Linux_headers__linux__64 = Linux_headers__debian
Linux_headers__linux__arm = Linux_headers__debian
Linux_headers__linux__arm__softfloat = Linux_headers__debian
Linux_headers__linux__arm__vfp = Linux_headers__debian
Linux_headers__linux__mipsel = Linux_headers__debian

class Linux_headers__linux__64 (Linux_headers):
    @context.subst_method
    def linux_arch (self):
        return 'x86_64'
    
class xLinux_headers__linux__64 (Linux_headers__debian):
# FIXME: we do not mirror all 12 debian arch's,
    source = 'http://ftp.debian.org/debian/pool/main/l/linux-kernel-headers/linux-kernel-headers_2.6.18-7_%(package_arch)s.deb&strip=0' 
