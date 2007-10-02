from gub import build
from gub import debian
from gub import mirrors

class Libc6 (build.BinaryBuild, build.SdkBuild):
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        self.with_template (version=debian.get_packages ()['libc6'].version (),
                   strip_components=0,
                   mirror=mirrors.glibc_deb,
# FIXME: we do not mirror all 12 debian arch's,
#                   mirror=mirrors.lilypondorg_deb,
                   format='deb')
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
