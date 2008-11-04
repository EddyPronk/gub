from gub import build
from gub import debian

class Libc6 (build.BinaryBuild, build.SdkBuild):
    source = 'http://ftp.debian.org/debian/pool/main/g/glibc/libc6__' + debian.get_packages ()['libc6'].version () + '_%(package_arch)s.deb&strip=0'
    def patch (self):
        self.system ('cd %(srcdir)s && rm -rf usr/sbin/ sbin/ bin/ usr/bin')
    def untar (self):
        build.BinaryBuild.untar (self)
        # Ugh, rewire absolute names and symlinks.
        i = self.expand ('%(srcdir)s/lib64')
        import os
        if os.path.islink (i):
            s = os.readlink (i)
            if s.startswith ('/'):
                os.remove (i)
                os.symlink (s[1:], i)
