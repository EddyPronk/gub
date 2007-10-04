from gub import build
from gub import mirrors

class Freebsd_runtime (build.BinaryBuild, build.SdkBuild):
    source = mirrors.with_template (name='freebsd-runtime', version='4.10-2', strip_components=0, mirror=mirrors.lilypondorg)
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        print 'FIXME:', __file__, ': strip-components'
        source.strip_components = 0
    def untar (self):
        build.BinaryBuild.untar (self)
    def patch (self):
        self.system ('rm -rf %(srcdir)s/usr/include/g++')

class Freebsd_runtime__64 (build.BinaryBuild, build.SdkBuild):
    source = mirrors.with_template (name='freebsd-runtime', version='6.2-1.amd64', strip_components=0, mirror=mirrors.lilypondorg)
