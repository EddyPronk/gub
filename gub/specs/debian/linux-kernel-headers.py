from gub import build
from gub import debian

class Linux_kernel_headers (build.BinaryBuild, build.SdkBuild):
    source = 'http://ftp.debian.org/debian/pool/main/l/linux-kernel-headers/linux-kernel-headers_2.5.999-test7-bk-17_%(package_arch)s.deb&strip=0' 
    def get_subpackage_names (self):
        return ['']
