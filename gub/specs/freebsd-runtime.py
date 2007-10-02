from gub import build
from gub import mirrors

class Freebsd_runtime (build.BinaryBuild, build.SdkBuild):
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        version = '4.10-2'
        if 0 and settings.target_architecture == 'i686-freebsd6':
            version = '6.1-RELEASE'
        if settings.target_architecture.startswith ('x86_64-freebsd'):
            version = '6.2-1.amd64'
    source = mirrors.with_template (name='freebsd-runtime', version=version, strip_components=0, mirror=mirrors.lilypondorg)
    def untar (self):
        build.BinaryBuild.untar (self)
    def patch (self):
        self.system ('rm -rf %(srcdir)s/usr/include/g++')
